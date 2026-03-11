.. _pygbuild_config_document_structure:

``structure`` subsection
========================

The ``structure`` section of the configuration file defines the document body
as an ordered list of **blocks**.  Each block is a YAML dictionary; the key
that is present determines the block type.

.. _source_blocks:

``source`` blocks
-----------------

Reads content from an external LaTeX file:

.. code-block:: yaml

    - source: introduction.tex

pygacity searches for the file first in the current working directory, then in
its bundled template directory.

``source`` blocks also accept substitutions, which replace ``<<<KEY>>>``
placeholders in the source file with specified values.  Two equivalent forms
are supported:

**Dictionary form:**

.. code-block:: yaml

    - source: introduction.tex
      substitutions:
          PROB_TITLE: "My Awesome Problem Set"
          SEMESTER: "Spring 2026"

**List form** (useful when order matters or a key appears more than once):

.. code-block:: yaml

    - source: introduction.tex
      substitutions:
          - search: PROB_TITLE
            replace: "My Awesome Problem Set"
          - search: SEMESTER
            replace: "Spring 2026"

.. _text_blocks:

``text`` blocks
-----------------

Injects a literal LaTeX string directly into the document:

.. code-block:: yaml

    - text: |
        \section{Introduction}
        This is the introduction to the document.

.. _pythontex_blocks:

``pythontex`` blocks
---------------------

Imports Python code into the document's pythontex kernel.  The value is a list
of named pygacity pythontex resources:

.. code-block:: yaml

    - pythontex:
        - setup

See :ref:`Python Resources <pythonresources>` for available resources.

.. _question_blocks:

Question blocks
---------------

A block with a ``question_number`` key is treated as a numbered exam or
assignment question.  It is rendered as an ``\item`` inside a LaTeX
``enumerate`` environment in the compiled document.  Question blocks must also
have a ``source`` key pointing to the LaTeX fragment for that question:

.. code-block:: yaml

    - question_number: 1
      source: problem1.tex
      points: 25
      group: 1

Additional optional keys:

``points``
    Integer point value.  When non-zero, the value is injected into the
    pythontex header as ``points`` and displayed in the compiled output.

``group``
    Integer group identifier used by the ``AnswerSet`` to organise answers into
    separate tables.

``config``
    Path to a YAML configuration file for ``short.tex``-style question pools.

Consecutive question blocks (i.e. blocks whose ``question_number`` is not
``None``) are automatically wrapped in a single ``\\begin{enumerate}`` …
``\\end{enumerate}`` in the output.

.. _enumerate_shorthand:

``enumerate`` shorthand (old-style)
------------------------------------

As a convenience, a list of question blocks can be expressed under a single
``enumerate`` key.  Question numbers are assigned sequentially starting from 1
(unless overridden with an explicit ``question_number``):

.. code-block:: yaml

    - enumerate:
        - source: problem1.tex
          points: 25
        - source: problem2.tex
          points: 25

This is exactly equivalent to:

.. code-block:: yaml

    - question_number: 1
      source: problem1.tex
      points: 25
    - question_number: 2
      source: problem2.tex
      points: 25

The shorthand is provided for backward compatibility.  New configurations
should use explicit ``question_number`` keys for clarity.
