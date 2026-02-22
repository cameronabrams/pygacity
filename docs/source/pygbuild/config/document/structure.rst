.. _pygbuild_config_document_structure:

``structure`` subsection
========================

The ``structure`` section of the configuration file describes the hierarchical structure of the document, including chapters, sections, subsections, and so on. It is represented as a nested list of dictionaries, where each dictionary represents a document element (termed a **block**) and its content.

Each block is formatted as a dictionary.  There are severl types of blocks, and block type is signified by the presence of specific keys in the dictionary.  The most common block types are ``source``, ``text``, ``pythontex``, ``enumerate``, and ``itemize``.

.. _source_blocks:

``source`` blocks
-----------------

This block type indicates that the content of the block is to be read from an external source file.  The value associated with the ``source`` key is a string specifying the path to the source file.  For example:

  .. code-block:: yaml

      - source: introduction.tex

This block will include the content of the file ``introduction.tex`` at this point in the document.

There are three source values that are treated specially by pygacity:

- ``header.tex``: If no file by this name exists in the working directory, pygacity uses a default version that comes packaged with pygacity.  The main thing to note about this header file is that it defines the document class as :ref:`autoprob <autoprob>` and includes several necessary packages.  
- ``short.tex``: This file is used to define macros and environments for short answer, multiple choice, fill-in-the-blank, and true-false questions.  If no file by this name exists in the working directory, pygacity uses a default version that comes packaged with pygacity.
- ``footer.tex``: If no file by this name exists in the working directory, pygacity uses a default version that comes packaged with pygacity.  The main thing to note about this footer file is that it ends the document with the ``\end{document}`` command.

``source`` blocks also permit user-defined substitutions, which replace placeholder
keys embedded in the source file with specified values.  Placeholder keys are
delimited by ``<<<`` and ``>>>`` in the source file, for example:

.. code-block:: latex

    \section{<<<PROB_TITLE>>>}

Substitutions can be specified in two equivalent forms in the YAML input.

**Dictionary form** — keys and values are given directly as a mapping:

.. code-block:: yaml

    - source: introduction.tex
      substitutions:
          PROB_TITLE: "My Awesome Problem Set"
          SEMESTER: "Spring 2026"

**List form** — each substitution is a two-key dictionary with ``search`` and
``replace`` entries.  This form is useful when the order of substitutions matters
or when the same key appears more than once:

.. code-block:: yaml

    - source: introduction.tex
      substitutions:
          - search: PROB_TITLE
            replace: "My Awesome Problem Set"
          - search: SEMESTER
            replace: "Spring 2026"

Both forms produce identical results.  Every ``<<<KEY>>>`` placeholder found in
the source file that has a matching entry in the substitution mapping will be
replaced with the corresponding value before the document is compiled.

.. _text_blocks:

``text`` blocks
-----------------

This block type indicates that the content of the block is to be included directly the the LaTex document at this point. The value associated with the ``text`` key is a string containing the LaTeX content to be included.  For example:

  .. code-block:: yaml

      - text: |
          \section{Introduction}
          This is the introduction to the document.

.. _pythontex_blocks:

``pythontex`` blocks
---------------------

This block declares a block that will import Python code so that it is available for use in subsequent ``pycode`` blocks. The value associated with the ``pythontex`` key is list of names of available pythontex resources in pygacity.  For example:

  .. code-block:: yaml

      - pythontex: 
        - setup

This block will make the all code defined in a package resource file called ``setup.pycode`` into the document's python kernel.  The python resources available in pygacity are described in the :ref:`Python Resources <pythonresources>` section of the documentation.

.. _enumerate_itemize_blocks:

``enumerate`` and ``itemize`` blocks
------------------------------------

These block types indicate that the content of the block is to be included as an enumerated or itemized list. The value associated with the ``enumerate`` or ``itemize`` key is a list of **blocks**. For examples:

  .. code-block:: yaml

      - enumerate:
        - source: problem1.tex
        - source: problem2.tex

This block will include an enumerated list where the first item is the content of ``problem1.tex`` and the second item is the content of ``problem2.tex``.  Below is an example of an itemized list:

  .. code-block:: yaml

      - itemize:
        - text: First item
        - text: Second item

``enumerate`` and ``itemize`` blocks are recursive, meaning that the items in the list can themselves be any type of block, including additional ``enumerate`` or ``itemize`` blocks.  For example:

  .. code-block:: yaml

      - enumerate:
        - text: First item
        - itemize:
          - text: Subitem 1
          - text: Subitem 2
        - text: Third item