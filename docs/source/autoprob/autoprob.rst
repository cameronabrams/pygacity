.. _autoprob:

The ``autoprob`` LaTeX Package
===============================

``pygacity`` uses its own custom LaTeX document class called ``autoprob`` to create assignment and exam documents.  This document class is built on top of the standard ``article`` document class, and includes several additional features specifically designed for creating problem-based documents.  The ``autoprob`` document class is included with the ``pygacity`` package, and is automatically used when building documents with ``pygacity``.  If you want to use it outside ``pygacity``, you can find the ``autoprob.cls`` file in the ``pygacity`` installation directory under ``resources/autoprob-package/tex/latex/autoprob.cls``.

LaTeX packages loaded by ``autoprob``:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Core packages
    - ``graphicx``
    - ``xcolor``
    - ``geometry`` (with margin=1in option)
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
    - ``tikz`` (along with the   tikz library)
    - ``listing``
    - ``pythontex``
- Others
    - ``hyperref``
    - ``enumitem``
    - ``fancyhdr``

Custom Commands in ``autoprob``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inline Code and Math Formatting
"""""""""""""""""""""""""""""""""

* ``\inl[options]`` - Inline code formatting with lstinline, using ``mypython`` style
* ``\molar{arg}`` - Add underbar accent to argument (for molar quantities)
* ``\parmol{arg1}{arg2}`` - Partial molar quantity: overline arg1 with subscript arg2

Thermodynamic Symbols (Molar Quantities)
"""""""""""""""""""""""""""""""""""""""""

* ``\Ub`` - Molar internal energy (U with underbar)
* ``\Hb`` - Molar enthalpy (H with underbar)
* ``\Sb`` - Molar entropy (S with underbar)
* ``\Vb`` - Molar volume (V with underbar)
* ``\Gb`` - Molar Gibbs energy (G with underbar)
* ``\thetab`` - Molar theta (θ with underbar)

Thermodynamic Operations
"""""""""""""""""""""""""""

* ``\dm{arg}`` - Delta mix subscript: Δ_mix arg
* ``\dr{arg}`` - Delta rxn subscript: Δ_rxn arg
* ``\df{arg}`` - Delta f superscript: Δ_f arg°

Common Thermodynamic Properties
"""""""""""""""""""""""""""""""""

* ``\hr`` - Standard enthalpy of reaction: Δ_rxn H°
* ``\gr`` - Standard Gibbs energy of reaction: Δ_rxn G°
* ``\hf`` - Standard enthalpy of formation: Δ_f H°
* ``\gf`` - Standard Gibbs energy of formation: Δ_f G°

Derivatives
"""""""""""

* ``\deriv{num}{denom}`` - Ordinary derivative: d(num)/d(denom)
* ``\pd{num}{denom}`` - Partial derivative: ∂(num)/∂(denom)
* ``\tpd{num}{denom}{const}`` - Partial derivative at constant: (∂num/∂denom)_const
* ``\ppd{num}{denom}`` - Second partial derivative: ∂²(num)/∂(denom)²

Other Symbols
"""""""""""""

* ``\pv`` - Vapor pressure: P^vap

Exam/Assignment Formatting
""""""""""""""""""""""""""""

* ``\tffillblank`` - True/false fill-in blank (underlined spaces)
* ``\tfitem{label}{answer}`` - True/false item with optional solution display
* ``\fitbfillblank`` - Fill-in-the-blank longer blank (underlined spaces)
* ``\fitanswerslot{answer}`` - Fill-in-the-blank answer slot with optional solution
* ``\mcchoiceitem{choice}{correct}`` - Multiple choice item with optional correct answer highlight

Document Metadata
"""""""""""""""""""

* ``\Universityname`` - University name (small caps, spaced)
* ``\Departmentname`` - Department name
* ``\Coursename`` - Course name
* ``\Termname`` - Term name (e.g., "Fall 2024")
* ``\Termcode`` - Term code
* ``\Instructorname`` - Instructor name
* ``\Instructoremail`` - Instructor email address
* ``\Subjectname`` - Subject name

Solutions Formatting
"""""""""""""""""""""

* ``\Solutionscolor`` - Color for solutions (blue)
* ``\Solutionstitle`` - "SOLUTIONS" title in solution color
* ``\Solutionheader`` - "SOLUTION" header in solution color

Document Headers
"""""""""""""""""""

* ``\plainheader{title}`` - Plain centered header with course info
* ``\asnheader{assignment}{due_date}`` - Assignment header with due date
* ``\examheader{exam_name}{date}`` - Exam header with name and date
* ``\qualifierheader{date}`` - PhD qualifying exam header

Problem/Question Management
"""""""""""""""""""""""""""

* ``\morespace{problem_num}`` - Add more space for a problem and clear page
* ``\examquestion{points}{file}`` - Include exam question from file with point value
* ``\qualquestion{file}{problem_num}`` - Include qualifier question with optional extra space
* ``\practicequestion{file}`` - Include practice question without extra space
* ``\problem{file}`` - Include problem from file

Special Effects
"""""""""""""""

* ``\cancelto[height]{to_value}{expression}`` - Draw diagonal arrow through expression pointing to a value (cancel-to notation)