# ThermoProblems
> A Python package to enable high-throughput generation of problems suitable for exams and problem sets for Thermodynamics courses

You may have learned how to use Python to solve thermodynamics problems, like equilibrium compositions for a reacting system, or phase compositions in vapor-liquid equilibrium.  `ThermoProblems` takes this idea and uses Python to generate new problems.  The problems are generated in such a way that they can be typeset into PDF's using LaTeX.  `ThermoProblems` relies on the `pythontex` package in LaTeX to allow Python code to run during document compilation and results of those calculations automatically included in the document.  `ThermoProblems` includes the pure-properties database that originally accompanied the textbook _Chemical, Biochemical, and Engineering Thermodynamics_ (4th edition) by Stan Sandler (Wiley, USA).

## Installation

`ThermoProblems` is in development.  Best to install it that way.

```sh
git clone git@github.com:cameronabrams/ThermoProblems.git
cd ThermoProblems
pip install -e .
```

`Thermoproblems` includes the LaTeX class file `autoprob.cls` under `[INSTALL-DIR]/thermoproblems/resources/autoprob-package/tex/latex/`.  All `latex` commands append this directory as a ``--include-directory`` argument.  If you would like to use `autoprob.cls` outside of `thermoproblems`, you will need to make your LaTeX installation aware of this directory.

## Release History

* 0.1.1
    * reorganized package
* 0.0.1
    * Initial version

## Meta

Cameron F. Abrams – cfa22@drexel.edu

Distributed under the MIT license. See ``LICENSE`` for more information.

[https://github.com/cameronabrams](https://github.com/cameronabrams/)

## Contributing

1. Fork it (<https://github.com/cameronabrams/ThermoProblems/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request
