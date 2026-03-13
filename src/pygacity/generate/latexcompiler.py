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
    latexmk : str
        path to latexmk executable
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
        self.latexmk = self.specs['paths']['latexmk']
        latexmkrc_spec = self.specs.get('paths', {}).get('latexmkrc')
        self.latexmkrc = Path(latexmkrc_spec).as_posix() if latexmkrc_spec else None
        self.pythontex = self.specs['paths']['pythontex']
        # explicit: latexmk -> pythontex -> latexmk
        # latexmkrc: single latexmk invocation, with pythontex orchestration in latexmkrc
        self.pythontex_workflow = self.specs.get('pythontex-workflow', 'latexmkrc')
        self.searchdirs = searchdirs
        self.output_dir: str = self.specs.get('paths', {}).get('build-dir', '.')
        self.cache_dir: str = self.specs.get('paths', {}).get('cache-dir', '.cache')
        self.job_name = self.specs.get('job-name', 'document')
        self.working_job_name = self.job_name
        self.FC = FileCollector()

    def _build_latexmk_command(
        self,
        includedirs: str,
        output_option: str,
        include_rc: bool = True,
    ) -> str:
        rc_option = f'-r "{self.latexmkrc}" ' if self.latexmkrc and include_rc else ''
        return (f'{self.latexmk} {rc_option}-xelatex -interaction=nonstopmode -file-line-error '
                f'-jobname={self.working_job_name} {includedirs} '
                f'{output_option} {self.working_job_name}.tex')

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
            include_dir = Path(d).as_posix()
            includedirs = includedirs + f' -latexoption="-include-directory={include_dir}"'
        logger.debug(f'includedirs {includedirs}')
        has_pycode = document.has_pycode
        output_option = ''
        if self.output_dir != '.':
            output_option = f'-outdir={self.output_dir}'
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

        use_rc = not (self.pythontex_workflow == 'latexmkrc' and not has_pycode)
        latexmk_command = self._build_latexmk_command(
            includedirs,
            output_option,
            include_rc=use_rc,
        )
        commands.append(Command(latexmk_command, ignore_codes=[1]))

        suffixes = ['.aux', '.log', '.out', '.pytxcode', '.fdb_latexmk', '.fls',    '.xdv']

        for suffix in suffixes:
            self.FC.append(f'{self.output_dir}/{self.working_job_name}{suffix}')
        if has_pycode:
            self.FC.append(f'{self.output_dir}/pythontex-files-{self.working_job_name}')
            if not is_solutions:
                self.FC.append(f'{self.output_dir}/pythontex-{serial}.log')
            else:
                self.FC.append(f'{self.output_dir}/pythontex-solutions-{serial}.log')

            if self.pythontex_workflow == 'latexmkrc':
                if not self.latexmkrc:
                    raise ValueError('pythontex-workflow "latexmkrc" requires build.paths.latexmkrc')
            elif self.pythontex_workflow == 'explicit':
                commands.append(Command(f'{self.pythontex} {self.output_dir}/{self.working_job_name}'))
                commands.append(Command(latexmk_command, ignore_codes=[1]))
            else:
                raise ValueError(f'Unknown pythontex-workflow "{self.pythontex_workflow}"; expected "explicit" or "latexmkrc"')
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
