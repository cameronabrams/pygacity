# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
LaTeX compilation functions for pygacity
"""
import logging

from pathlib import Path

from ..util.command import Command
from ..util.collectors import FileCollector
from .document import Document

logger = logging.getLogger(__name__)

class LatexCompiler:
    """ 
    LaTeX compiler class for building documents.
    
    Attributes
    ----------
    specs : dict
        build specifications
    pdflatex : str
        path to pdflatex executable
    pythontex : str
        path to pythontex executable
    searchdirs : list of str
        list of directories to search for included files (each prefixed with -include-directory=)
    output_dir : str
        output directory for compiled files (prefixed with -output-directory=)
    cache_dir : str
        cache directory for temporary files
    job_name : str
        base job name for output files (prefixed with -jobname=)
    working_job_name : str
        current working job name for output files
    FC : FileCollector
        file collector for tracking generated files
    """
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
        """
        Builds the list of commands needed to compile the document.
        
        Parameters
        ----------
        document : **Document**, optional
            the **Document** instance to compile (default is None)
            
        Returns
        -------
        list of Command
            list of **Command** instances to run for compilation
        """
        commands = []
        if not document:
            return commands
        serial = document.substitutions.get('serial', 0)
        serialstr = document.substitutions.get('serialstr', str(serial) if isinstance(serial, int) else serial)
        is_solutions = document.substitutions.get('solutions', False)
        self.working_job_name = self.job_name
        if isinstance(serial, int) and serial > 0:
            self.working_job_name = self.job_name + f'-{serialstr}'
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
            if not is_solutions:
                self.FC.append(f'{self.output_dir}/pythontex-{serial}.log')
            else:
                self.FC.append(f'{self.output_dir}/pythontex-solutions-{serial}.log')
            commands.append(Command(f'{self.pythontex} {self.output_dir}/{self.working_job_name}'))

        commands.append(Command(repeated_command, ignore_codes=[1]))
        return commands

    def build_document(self, document: Document = None, cleanup: bool = False):
        """
        Builds the specified document by running the necessary commands.
        
        Parameters
        ----------
        document : **Document**, optional
            the **Document** instance to compile (default is None)
        cleanup : bool, optional
            if True, deletes intermediate files after build (default is False)
            """
        commands = self.build_commands(document)
        for c in commands:
            logger.debug(f'Running command: {c.c}')
            out, err = c.run()
            logger.debug(f'Command output:\n{out}\n\n')
            logger.debug(f'Command error:\n{err}\n\n')
        if cleanup:            
            self.FC.flush()
