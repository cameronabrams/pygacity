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

Then, you need to add the TeX tree under `Autoprob` to the TeXLive list of auxiliary trees:

```sh
tlmgr conf auxtrees add "path-to-ThermoProblems/Autoprob"
```


## Usage example

Consider the following file `Example1.tex`:
```
\input{SimpleHeader}
\begin{pycode}
from ThermoProblems.Chem.Properties import PureProperties
Prop=PureProperties()
A=Prop.get_compound('n-butane')
restr=A.report_as_tex()
\end{pycode}
\begin{document}
\noindent Here is some information about \py{A.name}:\\*[2em]
\py{restr}
\end{document}
```
Compiling this like so:
```sh
pdflatex Example1
pythontex Example1
pdflatex Example1
```
yields:

![](docs/Example1-PDFshot.png)

## Release History

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
