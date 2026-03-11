.. _pygbuild_config_document_preamble:

``preamble`` subsection
=======================

The optional ``preamble`` subsection supplies LaTeX code that is injected into
the generated document immediately before ``\begin{document}``.  It accepts
three forms.

String form (literal LaTeX)
---------------------------

A plain YAML string is inserted verbatim:

.. code-block:: yaml

    document:
      preamble: |
        \usepackage[T1]{fontenc}
        \usepackage{lato}
        \renewcommand{\familydefault}{\sfdefault}

This form gives full control but suppresses all pygacity defaults — nothing
extra is added.

Absent / ``null``
-----------------

If ``preamble`` is omitted entirely or set to ``~``, pygacity applies its
built-in defaults: the ``default`` font and the ``default`` pagestyle (see
below).

Structured dict form
--------------------

The most flexible form is a mapping with up to three sub-keys: ``font``,
``pagestyle``, and ``commands``.  Each is optional; ``font`` and ``pagestyle``
default to ``"default"`` when absent.

.. code-block:: yaml

    document:
      preamble:
        font: default
        pagestyle: default
        commands:
          Universityname: Drexel University
          Coursename: CHE 230 - Thermodynamics I

``font``
^^^^^^^^

Controls the font preamble.  Accepted values:

``"default"`` *(default when absent)*
    Loads TeX Gyre Heros (a metric-compatible Helvetica substitute) and sets it
    as the document default:

    .. code-block:: latex

        \usepackage[T1]{fontenc}
        \usepackage{tgheros}
        \renewcommand{\familydefault}{\sfdefault}

``"example"``
    Loads an alternative bundled font configuration.

*literal LaTeX string*
    Any other string is inserted verbatim, e.g.:

    .. code-block:: yaml

        font: |
          \usepackage{lato}
          \renewcommand{\familydefault}{\sfdefault}

*dict with* ``input`` *key*
    Reads font preamble from a local file:

    .. code-block:: yaml

        font:
          input: my_font.tex

``~`` *(null)*
    Suppresses the default entirely — no font preamble is added.

``pagestyle``
^^^^^^^^^^^^^

Controls the page-style preamble.  Accepted values follow the same pattern as
``font``:

``"default"`` *(default when absent)*
    Sets up ``fancyhdr`` with the course name and serial number in the header
    and the page number in the footer:

    .. code-block:: latex

        \pagestyle{fancy}
        \fancyhf{}
        \lhead{\footnotesize \Universityname\ --- \Coursename\ --- \Termname}
        \rhead{\footnotesize <<<serialstr>>>}
        \rfoot{\thepage}

    ``<<<serialstr>>>`` is replaced by pygacity at build time with the
    document's serial-number string.

``~`` *(null)*
    Suppresses the default — no page-style setup is added.  Use this when your
    document class handles headers and footers itself.

``commands``
^^^^^^^^^^^^

A mapping of autoprob class variable names to values.  Each entry becomes a
``\renewcommand`` in the preamble:

.. code-block:: yaml

    commands:
      Universityname: Drexel University
      Departmentname: Chemical & Biological Engineering
      Instructorname: A. N. Other
      Instructoremail: ano@drexel.edu
      Coursename: CHE 230 - Thermodynamics I
      Termcode: 202535
      Termname: Spring 2025

Only commands that are defined as zero-argument ``\newcommand`` entries in
``autoprob.cls`` are permitted.  pygacity raises a ``ValueError`` at startup
if an unknown command name is supplied.

Typical full example
--------------------

This is the pattern used by the bundled examples — suppress the built-in font
and pagestyle so they are fully controlled by the ``commands`` block and any
additional LaTeX in the class:

.. code-block:: yaml

    document:
      preamble:
        font: ~
        pagestyle: ~
        commands:
          Universityname: University of Nowhere
          Departmentname: Mechanical Engineering
          Instructorname: Eustace T. Smartypants
          Instructoremail: ets@unow.edu
          Coursename: BIO 5678 - Applied Pyrohydrodynamics
          Termcode: 202525
          Termname: Winter 2025-2026
