import logging

from pathlib import Path

from ..util.command import Command
from ..util.collectors import FileCollector
from .document import Document

logger = logging.getLogger(__name__)

class LatexCompiler:
    
    def __init__(self, build_specs: dict, searchdirs: list = []):
        self.specs = build_specs
        self.pdflatex = self.specs['paths']['pdflatex']
        self.pythontex = self.specs['paths']['pythontex']
        self.searchdirs = searchdirs
        self.output_dir: str = self.specs.get('paths', {}).get('build-dir', '.')
        self.cache_dir: str = self.specs.get('paths', {}).get('cache-dir', '.cache')
        self.job_name = self.specs.get('job-name', 'document')
        self.working_job_name = self.job_name
        self.FC = FileCollector()

    def build_commands(self, document: Document = None):
        commands = []
        if not document:
            return commands
        serial = document.substitutions.get('serial', 0)
        self.working_job_name = self.job_name
        if isinstance(serial, int) and serial > 0:
            self.working_job_name = self.job_name + f'-{serial}'
        document.write_source(local_output_name=self.working_job_name)
        includedirs = ''
        for d in self.searchdirs:
            includedirs = includedirs + ' -include-directory=' + str(d)
        logger.debug(f'includedirs {includedirs}')
        has_pycode = document.has_pycode
        output_option = ''
        if self.output_dir != '.':
            output_option = f'-output-directory={self.output_dir}'
        build_path = Path.cwd() / self.output_dir
        
        if self.output_dir != '.':
            # find any configs referenced in document blocks and copy them to output_dir
            for block in document.blocks:
                file_or_files_or_none = block.copy_referenced_configs(build_path)
                if file_or_files_or_none:
                    if isinstance(file_or_files_or_none, list):
                        for f in file_or_files_or_none:
                            self.FC.append(f)
                    else:
                        self.FC.append(file_or_files_or_none)

        repeated_command = (f'{self.pdflatex} -interaction=nonstopmode -file-line-error '
                                f'-jobname={self.working_job_name} {includedirs} '
                                f'{output_option} {self.working_job_name}.tex')
        commands.append(Command(repeated_command, ignore_codes=[1]))

        self.FC.append(f'{self.output_dir}/{self.working_job_name}.aux')
        self.FC.append(f'{self.output_dir}/{self.working_job_name}.log')
        self.FC.append(f'{self.output_dir}/{self.working_job_name}.out')
        self.FC.append(f'{self.output_dir}/{self.working_job_name}.pytxcode')
        if has_pycode:
            self.FC.append(f'{self.output_dir}/pythontex-files-{self.working_job_name}')
            self.FC.append(f'{self.output_dir}/pythontex-{serial}.log')
            commands.append(Command(f'{self.pythontex} {self.output_dir}/{self.working_job_name}'))

        commands.append(Command(repeated_command, ignore_codes=[1]))
        return commands

    def build_document(self, document=None, cleanup=False):
        commands = self.build_commands(document)
        for c in commands:
            logger.debug(f'Running command: {c.c}')
            out, err = c.run()
            logger.debug(f'Command output:\n{out}\n\n')
            logger.debug(f'Command error:\n{err}\n\n')
        if cleanup:            
            self.FC.flush()
