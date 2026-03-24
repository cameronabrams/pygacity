# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
LaTeX compilation functions for pygacity
"""
import logging
import os
import re

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
        self._pythontex_log: str | None = None

    def _build_latexmk_command(
        self,
        source_name: str,
        include_rc: bool = True,
        outdir: str = None,
    ) -> str:
        rc_option = f'-r "{self.latexmkrc}" ' if self.latexmkrc and include_rc else ''
        outdir_option = f'"-outdir={outdir}" ' if outdir else ''
        return (f'{self.latexmk} {rc_option}-xelatex -interaction=nonstopmode -file-line-error '
                f'"-jobname={self.working_job_name}" '
                f'{outdir_option}"{source_name}"')

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
        build_path = Path.cwd() / self.output_dir
        if self.output_dir != '.':
            source_path = build_path / f'{self.working_job_name}.tex'
        else:
            source_path = Path(f'{self.working_job_name}.tex')
        document.write_source(local_output_name=str(source_path.with_suffix('')))

        # Build TEXINPUTS so xelatex can find included files regardless of spaces/parens in paths.
        # TEXINPUTS entries are separated by os.pathsep; a trailing separator tells TeX to
        # append the default search path after our explicit entries.
        texinputs_dirs = [str(Path(d)) for d in self.searchdirs]
        if self.output_dir != '.':
            texinputs_dirs.append(str(Path.cwd()))
        texinputs = os.pathsep.join(texinputs_dirs) + os.pathsep
        logger.debug(f'TEXINPUTS {texinputs}')
        has_pycode = document.has_pycode

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

        # Run latexmk from the build directory with just the bare filename so that
        # xelatex never sees a path containing spaces or parentheses.
        if self.output_dir != '.':
            latexmk_cwd = str(build_path)
            latexmk_source = f'{self.working_job_name}.tex'
            latexmk_outdir = None  # already running inside the output dir
            pytx_target = self.working_job_name
        else:
            latexmk_cwd = None
            latexmk_source = source_path.as_posix()
            latexmk_outdir = None
            pytx_target = self.working_job_name

        use_rc = not (self.pythontex_workflow == 'latexmkrc' and not has_pycode)
        latexmk_command = self._build_latexmk_command(
            latexmk_source,
            include_rc=use_rc,
            outdir=latexmk_outdir,
        )
        commands.append(Command(latexmk_command, ignore_codes=[1], env={'TEXINPUTS': texinputs}, cwd=latexmk_cwd))

        suffixes = ['.aux', '.log', '.out', '.pytxcode', '.fdb_latexmk', '.fls',    '.xdv']

        for suffix in suffixes:
            self.FC.append(f'{self.output_dir}/{self.working_job_name}{suffix}')
        if has_pycode:
            self.FC.append(f'{self.output_dir}/pythontex-files-{self.working_job_name}')
            if not is_solutions:
                pytx_log = f'{self.output_dir}/pythontex-{serialstr}.log'
            else:
                pytx_log = f'{self.output_dir}/pythontex-solutions-{serialstr}.log'
            self.FC.append(pytx_log)
            self._pythontex_log = pytx_log

            if self.pythontex_workflow == 'latexmkrc':
                if not self.latexmkrc:
                    raise ValueError('pythontex-workflow "latexmkrc" requires build.paths.latexmkrc')
            elif self.pythontex_workflow == 'explicit':
                commands.append(Command(f'{self.pythontex} "{pytx_target}"', env={'TEXINPUTS': texinputs}, cwd=latexmk_cwd))
                commands.append(Command(latexmk_command, ignore_codes=[1], env={'TEXINPUTS': texinputs}, cwd=latexmk_cwd))
            else:
                raise ValueError(f'Unknown pythontex-workflow "{self.pythontex_workflow}"; expected "explicit" or "latexmkrc"')
        return commands

    def _check_pythontex_log(self):
        """Parse the PythonTeX log and emit logger.error for any reported errors."""
        if not self._pythontex_log:
            return
        log_path = Path(self._pythontex_log)
        if not log_path.exists():
            return
        content = log_path.read_text(encoding='utf-8', errors='replace')
        match = re.search(r'PythonTeX:\s+\S+\s+-\s+(\d+)\s+error', content)
        if not match or int(match.group(1)) == 0:
            return
        n_errors = int(match.group(1))
        logger.error(f'PythonTeX reported {n_errors} error(s) in {log_path}')
        # Extract each message block (between -----...---- delimiters)
        for block in re.findall(r'(-----[^\n]*\n.*?---+)', content, re.DOTALL):
            if re.search(r'traceback|error', block, re.IGNORECASE):
                logger.error(block.strip())

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
        self._check_pythontex_log()
        if cleanup:
            self.FC.flush()
