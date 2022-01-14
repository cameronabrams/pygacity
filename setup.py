import pathlib
from setuptools import setup
# The directory containing this file
HERE = pathlib.Path(__file__).parent
# The text of the README file
README = (HERE / "README.md").read_text()
setup(
      name='ThermoProblems',
      version='0.0.1',
      description='Routines for solving problems in thermodynamics',
      url='github.com/cameronabrams/ThermoProblems',
      author='Cameron F. Abrams',
      author_email='cfa22@drexel.edu',
      license='MIT',
      packages=['ThermoProblems','ThermoProblems.Chem','tests'],
      include_package_data=True
)