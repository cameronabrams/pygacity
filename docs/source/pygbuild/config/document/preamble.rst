.. _pygbuild_config_document_preamble:

``preamble`` subsection
=======================

The ``preamble`` section of the configuration file is an optional section that allows the user to specify custom LaTeX code to be included in the preamble of the generated document. This section is represented as a single string containing valid LaTeX code.

This code will be inserted into the LaTeX document before the ``\begin{document}`` command, allowing the user to customize the document's appearance and behavior by including additional packages, defining new commands, or setting document options.

For example, a user might include the following LaTeX code in the ``preamble`` section to change the default font of the document:

.. code-block:: yaml

    preamble: |
        \usepackage[T1]{fontenc}
        \usepackage{tgheros}
        \renewcommand{\sfdefault}{qhv} % TeX Gyre Heros family name
        \renewcommand{\familydefault}{\sfdefault}

This would set the document's default font to TeX Gyre Heros.
If the ``preamble`` section is not specified in the configuration file, a default preamble will be used.