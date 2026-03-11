# Author: Cameron F. Abrams, <cfa22@drexel.edu>
"""
Simple command runner
"""
import subprocess
import logging

logger = logging.getLogger(__name__)

class Command:
    def __init__(self, command: str, ignore_codes: list[int] = [], timeout: int = 120, **options):
        """
        Initializes the Command instance.

        Parameters
        ----------
        command : str
            the base command to run
        ignore_codes : list of int, optional
            list of return codes to ignore (default is empty list)
        timeout : int, optional
            seconds to wait before killing the process (default is 120)
        options : dict
            command-line options as key-value pairs
        """
        self.command = command
        self.ignore_codes = ignore_codes
        self.timeout = timeout
        self.options = options
        self.c = f'{self.command} ' + ' '.join([f'-{k} {v}' for k, v in self.options.items()])

    def run(self):
        """
        Runs the command and returns the output and error messages.

        Raises
        ------
        subprocess.TimeoutExpired
            if the process does not finish within ``self.timeout`` seconds;
            the process is killed before the exception propagates
        subprocess.SubprocessError
            if the process exits with a non-zero return code that is not in
            ``self.ignore_codes``
        """
        process = subprocess.Popen(self.c, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            out, err = process.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()  # drain pipes so the child is fully reaped
            raise subprocess.TimeoutExpired(
                self.c, self.timeout,
                output=f'Command "{self.c}" timed out after {self.timeout} s and was killed'
            )
        if process.returncode != 0 and not process.returncode in self.ignore_codes:
            if out.strip():
                logger.error(f'stdout from "{self.command}":\n{out}')
            if err.strip():
                logger.error(f'stderr from "{self.command}":\n{err}')
            raise subprocess.SubprocessError(f'Command "{self.c}" failed with returncode {process.returncode}')
        return out, err