.. _autoprob:

The autoprob LaTeX Package
==========================

``pygacity`` uses its own custom LaTeX document class called ``autoprob`` to create assignment and exam documents.  This document class is built on top of the standard ``article`` document class, and includes several additional features specifically designed for creating problem-based documents.  The ``autoprob`` document class is included with the ``pygacity`` package, and is automatically used when building documents with ``pygacity``.  If you want to use it outside ``pygacity``, you can find the ``autoprob.cls`` file in the ``pygacity`` installation directory under ``resources/autoprob-package/tex/latex/autoprob.cls``.

Document Class Options
~~~~~~~~~~~~~~~~~~~~~~

``autoprob`` accepts the following options via ``\documentclass[...]{autoprob}``:

* ``solutions`` — sets the ``\ifshowsolutions`` flag to true; solution content guarded by ``\ifshowsolutions`` … ``\fi`` is rendered.
* ``answers`` — sets the ``\ifshowanswers`` flag to true.
* ``givespace`` — sets the ``\ifgivespace`` flag to true; extra blank space is added after questions to give students room to work.

Any other option is passed through to the underlying ``article`` class.

LaTeX packages loaded by ``autoprob``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Core packages
    - ``graphicx``
    - ``xcolor``
    - ``geometry`` (with ``margin=1in`` option)
    - ``calc``
- Math packages
    - ``amsmath``
    - ``amssymb``
    - ``amsfonts``
    - ``amstext``
    - ``mathtools``
    - ``latexsym``
    - ``euscript`` (with ``mathscr`` option)
    - ``nccmath``
    - ``accents``
    - ``mhchem`` (version 4)
- Utility packages
    - ``xifthen``
    - ``xfp``
    - ``currfile``
    - ``datatool``
    - ``soul``
- Table packages
    - ``array``
    - ``multirow``
    - ``longtable``
    - ``booktabs``
    - ``caption`` (``font=small``, ``labelfont=bf`` options)
- Graphics and coding
    - ``tikz`` (with the ``patterns`` library)
    - ``listings``
    - ``pythontex``
    - ``tcolorbox``
- Lists and headers
    - ``enumitem``
    - ``fancyhdr``
- ``hyperref`` (loaded last)

Custom Commands in ``autoprob``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inline Code and Math Formatting
"""""""""""""""""""""""""""""""""

* ``\inl[options]`` — Inline code formatting with ``lstinline``, using ``mypython`` style.
* ``\molar{arg}`` — Add underbar accent to argument (for molar quantities).
* ``\parmol{arg1}{arg2}`` — Partial molar quantity: overline *arg1* with subscript *arg2*.

Pint Quantity Formatting
"""""""""""""""""""""""""

These commands embed a ``pint.Quantity`` (or any Python value) in the typeset output via pythontex ``\py{}``, with a configurable number of decimal places (default 2):

* ``\pyff[n]{expr}`` — Plain float: ``f'{expr:.nf}'``
* ``\pypl[n]{expr}`` — Pint LaTeX format: ``f'{expr:.nf~L}'`` (renders units in LaTeX math notation)
* ``\pypp[n]{expr}`` — Pint pretty-print format: ``f'{expr:.nf~P}'`` (renders units in Unicode notation)

Thermodynamic Symbols (Molar Quantities)
"""""""""""""""""""""""""""""""""""""""""

* ``\Ub`` — Molar internal energy (U with underbar)
* ``\Hb`` — Molar enthalpy (H with underbar)
* ``\Sb`` — Molar entropy (S with underbar)
* ``\Vb`` — Molar volume (V with underbar)
* ``\Gb`` — Molar Gibbs energy (G with underbar)
* ``\thetab`` — Molar theta (θ with underbar)

Thermodynamic Operations
"""""""""""""""""""""""""""

* ``\dm{arg}`` — Delta mix subscript: Δ\ :sub:`mix` *arg*
* ``\dr{arg}`` — Delta rxn subscript: Δ\ :sub:`rxn` *arg*
* ``\df{arg}`` — Delta f superscript: Δ\ :sub:`f` *arg*\ °

Common Thermodynamic Properties
"""""""""""""""""""""""""""""""""

* ``\hr`` — Standard enthalpy of reaction: Δ\ :sub:`rxn` H°
* ``\gr`` — Standard Gibbs energy of reaction: Δ\ :sub:`rxn` G°
* ``\hf`` — Standard enthalpy of formation: Δ\ :sub:`f` H°
* ``\gf`` — Standard Gibbs energy of formation: Δ\ :sub:`f` G°

Derivatives
"""""""""""

* ``\deriv{num}{denom}`` — Ordinary derivative: d(*num*)/d(*denom*)
* ``\pd{num}{denom}`` — Partial derivative: ∂(*num*)/∂(*denom*)
* ``\tpd{num}{denom}{const}`` — Partial derivative at constant: (∂*num*/∂*denom*)\ :sub:`const`
* ``\ppd{num}{denom}`` — Second partial derivative: ∂²(*num*)/∂(*denom*)²

Other Symbols
"""""""""""""

* ``\pv`` — Vapor pressure: P\ :sup:`vap`

Exam/Assignment Formatting
""""""""""""""""""""""""""""

* ``\tffillblank`` — True/false fill-in blank (short underlined rule)
* ``\tfitem{label}{answer}`` — True/false item; shows *answer* in blue when solutions are on
* ``\fitbfillblank`` — Fill-in-the-blank longer blank (underlined spaces)
* ``\fitanswerslot{answer}`` — Fill-in-the-blank answer slot; shows *answer* in blue when solutions are on
* ``\mcchoiceitem{choice}{correct}`` — Multiple-choice item; boxes and highlights *choice* in blue when it equals *correct* and solutions are on

Document Metadata
"""""""""""""""""""

These zero-argument commands carry document identity strings used by the header commands.  They are intended to be redefined via ``\renewcommand`` in the preamble (or via the ``commands`` sub-key of the pygacity ``preamble`` configuration):

* ``\Universityname`` — University name (default: small-caps spaced placeholder)
* ``\Departmentname`` — Department name
* ``\Coursename`` — Course name
* ``\Termname`` — Term name (e.g., "Fall 2024")
* ``\Termcode`` — Term code
* ``\Instructorname`` — Instructor name
* ``\Instructoremail`` — Instructor email address
* ``\Subjectname`` — Subject name

Solutions Formatting
"""""""""""""""""""""

* ``\Solutionscolor`` — Color used for solution text (default: ``blue``)
* ``\Solutionstitle`` — "SOLUTIONS" rendered in ``\Solutionscolor`` small-caps spaced text
* ``\Solutionheader`` — "SOLUTION" rendered in ``\Solutionscolor`` small-caps text

Document Headers
"""""""""""""""""""

* ``\plainheader{title}`` — Centered header with university, department, course/term info, and *title*
* ``\asnheader{assignment}{due_date}`` — Assignment header including due date; appends ``\Solutionstitle`` when solutions are on
* ``\examheader{exam_name}{date}`` — Exam header with instructor contact; appends ``\Solutionstitle`` when solutions are on
* ``\qualifierheader{date}`` — PhD qualifying exam header using ``\Subjectname``

Environments
""""""""""""

* ``fmpage{width}`` — A framed minipage: wraps content in a box of the given width.

Special Effects
"""""""""""""""

* ``\cancelto[height]{to_value}{expression}`` — Draw a diagonal arrow through *expression* pointing to *to_value* (cancel-to notation), using TikZ.
