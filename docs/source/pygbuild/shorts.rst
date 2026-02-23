.. _shorts:

Working with Short-Answer, Multiple-Choice, Fill-in-the-Blank, and True/False Questions
========================================================================================

The ``short.tex`` template (located in ``pygacity/resources/templates/``) provides
a flexible, data-driven mechanism for authoring question pools of four types:

* **Short answer** — a question with space for a written response
* **Multiple choice** — a question with labeled lettered choices
* **Fill in the blank** — a sentence with one or more blanks to complete
* **True/False** — a statement the student marks T or F

Rather than encoding questions directly in LaTeX, you write them in a YAML file
and reference it from the document config.  ``short.tex`` handles typesetting,
per-serial shuffling, solution display, and answer registration automatically.

Referencing ``short.tex`` from a Config
-----------------------------------------

Use ``short.tex`` as a ``source`` entry in the ``enumerate`` block of your
document YAML.  Add a ``config`` key pointing to the YAML file that contains
the question pool:

.. code-block:: yaml

    - enumerate:
      - source: short.tex
        points: 30
        config: derivatives_short_answer.yaml
        group: 2
      - source: short.tex
        points: 10
        config: true_false_questions.yaml
        group: 4

The same ``short.tex`` template can appear multiple times — once per question
pool.  Each entry gets its own ``points`` value, ``group`` assignment, and
independent YAML file.

If you are building in a subdirectory, prepend ``../`` to the config filename:

.. code-block:: yaml

      - source: short.tex
        config: ../my_questions.yaml

The Question-Pool YAML File
----------------------------

The YAML file has two top-level keys: ``config`` (pool-level settings) and
``content`` (the list of individual questions).

.. code-block:: yaml

    config:
      count: 3           # how many questions to draw from the pool
      shuffle: true      # shuffle the pool before drawing (per serial)
      type: short_answer # default question type for items that omit 'T'
      instructions: |
        \textbf{Derivatives.} Provide the correct derivative for each function.
      shuffle_choices: false  # (multiple_choice only) shuffle choices globally
      clearpage: true         # emit \clearpage after the question block (default: true)
    content:
      - Q: \(f(x) = x^2\)
        A: \(f^\prime(x) = 2x\)
        text: The power rule states that the derivative of \(x^n\) is \(nx^{n-1}\).
      - Q: \(f(x) = \sin(x)\)
        A: \(f^\prime(x) = \cos(x)\)
        text: The derivative of \(\sin(x)\) is \(\cos(x)\).

If the YAML file contains only a flat list (no ``config``/``content`` split),
all questions in the list are used without shuffling.

``config`` Keys
~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 10 70
   :header-rows: 1

   * - Key
     - Default
     - Description
   * - ``count``
     - all
     - Number of questions to draw from ``content``.  Questions are drawn from
       the top of the (possibly shuffled) list.
   * - ``shuffle``
     - ``false``
     - When ``true``, the pool is shuffled per serial before ``count`` questions
       are drawn.  Because ``serial`` seeds the RNG, the same serial always
       produces the same draw.
   * - ``type``
     - ``fill_in_the_blank``
     - Default question type applied to any item that omits the ``T`` key.
       One of ``short_answer``, ``multiple_choice``, ``fill_in_the_blank``, or
       ``true_false``.
   * - ``instructions``
     - built-in string
     - Instruction text printed above the question list.  LaTeX markup is
       supported.  The ``points`` value from the document config is prepended
       automatically (e.g. ``(30 pts.)``).
   * - ``shuffle_choices``
     - ``false``
     - ``multiple_choice`` only.  When ``true``, the lettered choices for each
       MC question are shuffled per serial.  The correct answer label (``A``)
       is updated automatically to track the shuffled position.
   * - ``clearpage``
     - ``true``
     - When ``true``, ``\clearpage`` is emitted after the question block.

Question Item Keys
~~~~~~~~~~~~~~~~~~~

Each entry in ``content`` is a dict with the following keys:

.. list-table::
   :widths: 20 10 70
   :header-rows: 1

   * - Key
     - Required
     - Description
   * - ``Q``
     - yes
     - Question text.  LaTeX markup is supported.  For ``fill_in_the_blank``,
       use ``___`` (three underscores) to mark the blank; ``short.tex`` replaces
       it with ``\fitanswerslot{answer}`` which renders as a dashed line in the
       student copy and shows the answer inline in the solution copy.
   * - ``A``
     - yes
     - The correct answer.  For ``multiple_choice`` this is the label of the
       correct choice (e.g. ``B``).  For ``true_false`` this is ``T`` or ``F``.
       For ``short_answer`` and ``fill_in_the_blank`` this is the answer string
       (LaTeX markup supported).
   * - ``T``
     - no
     - Question type override.  One of ``short_answer``, ``multiple_choice``,
       ``fill_in_the_blank``, or ``true_false``.  When omitted, the pool-level
       ``type`` is used.
   * - ``text``
     - no
     - Explanation shown in the solution copy (in red).  LaTeX markup supported.
   * - ``choices``
     - MC only
     - Ordered dict of ``label: text`` pairs for a ``multiple_choice`` question.
       Labels are typically ``A``, ``B``, ``C``, ``D`` but can be any strings.
   * - ``shuffle_choices``
     - no
     - Per-question override of the pool-level ``shuffle_choices``.  Set to
       ``false`` to prevent shuffling on a question whose choices cross-reference
       each other by label (e.g. ``"Both A and B are correct."``).
   * - ``fixed_last``
     - no
     - ``multiple_choice`` only.  When ``true``, the last choice is pinned in
       its position while all other choices are shuffled freely.  Useful for
       "None of the above" or "All of the above" choices.

Question Types in Detail
-------------------------

Short Answer (``short_answer``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A question followed by blank space for a written response.

.. code-block:: yaml

    - Q: \(f(x) = \ln(x)\)
      A: \(f^\prime(x) = \frac{1}{x}\)
      text: The derivative of \(\ln(x)\) is \(\frac{1}{x}\).

In the student copy, 1.4 cm of blank space appears below the question.
In the solution copy, the answer is shown in blue and the explanation in red.

Fill in the Blank (``fill_in_the_blank``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A sentence with a blank marked by ``___``.  The answer is rendered via
``\fitanswerslot``: a dashed line in the student copy and the answer text inline
in the solution copy.

.. code-block:: yaml

    - Q: The capital of France is ___.
      A: Paris
      text: Paris has been the capital of France since the 10th century.

Multiple blanks in a single question are supported — use ``___`` once per blank
and provide a single combined answer string.

True/False (``true_false``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A statement the student marks T or F, rendered via the ``\tfitem`` LaTeX macro.

.. code-block:: yaml

    - Q: The chemical symbol for gold is Ag.
      A: F
      text: The chemical symbol for gold is Au; Ag is the symbol for silver.

Multiple Choice (``multiple_choice``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A question with lettered choices rendered via the ``\mcchoiceitem`` LaTeX macro.
The correct choice label is stored in ``A``; in the solution copy the correct
choice is highlighted.

.. code-block:: yaml

    - Q: Which planet is known as the Red Planet?
      choices:
        A: Venus
        B: Mars
        C: Jupiter
        D: Saturn
      A: B
      text: Mars is known as the Red Planet due to iron oxide on its surface.

With ``shuffle_choices: true`` in the pool config, choice *texts* are shuffled
and ``A`` is updated automatically to point to whichever label now carries the
correct text.

**Per-question shuffle override** — when choices cross-reference each other
(e.g. "Both A and B are correct"), set ``shuffle_choices: false`` on that item:

.. code-block:: yaml

    - Q: "Which statements about Newton's laws are correct? (Select the best answer.)"
      shuffle_choices: false
      choices:
        A: The first law states that an object at rest stays at rest unless acted on by a net force.
        B: The second law states that F = ma.
        C: Both A and B are correct.
        D: Neither A nor B is correct.
      A: C
      text: Both A and B are correct; shuffling would invalidate the cross-references.

**Pinning the last choice** — use ``fixed_last: true`` to keep "None of the above"
or similar choices at the bottom while the rest are shuffled freely:

.. code-block:: yaml

    - Q: Which of the following is a fossil fuel?
      fixed_last: true
      choices:
        A: Solar energy
        B: Wind energy
        C: Natural gas
        D: None of the above.
      A: C
      text: Natural gas is a fossil fuel. The last choice is pinned in place.

Shuffling and Reproducibility
-------------------------------

When ``shuffle: true``, the question pool is shuffled using ``rng`` — the
per-serial NumPy RNG that is seeded by the serial number in ``setup.py``.
Likewise, ``shuffle_choices: true`` shuffles MC choices using the same ``rng``.
Because the RNG state is deterministic given the serial, the same serial always
produces the same question draw and the same choice ordering, making every build
fully reproducible.

Answer Registration
--------------------

After selecting and processing questions, ``short.tex`` registers each answer
with ``AnsSet``:

.. code-block:: python

    for l, t in zip([chr(ord('a') + x) for x in range(len(answers))], answers):
        AnsSet.register(idx, group=group, label=l, value=t)

The labels are ``a``, ``b``, ``c``, … in draw order.  These answers appear in
the consolidated answer set document, one column per question and one row per
serial.

Complete Examples
------------------

The ``compound_exam`` example uses ``short.tex`` four times, exercising all four
question types.  The relevant section of ``CompoundExam.yaml``:

.. literalinclude:: ../../../examples/compound_exam/CompoundExam.yaml
    :language: yaml
    :lines: 30-48

The corresponding pool files:

**Short answer** — 8 questions in pool, 3 drawn per serial, shuffled:

.. literalinclude:: ../../../examples/compound_exam/derivatives_short_answer.yaml
    :language: yaml

**Fill in the blank** — 11 questions in pool, 4 drawn per serial, shuffled:

.. literalinclude:: ../../../examples/compound_exam/geography_fill_in_the_blank.yaml
    :language: yaml

**True/False** — 8 questions in pool, 4 drawn per serial, shuffled:

.. literalinclude:: ../../../examples/compound_exam/true_false_questions.yaml
    :language: yaml

**Multiple choice** — 13 questions in pool, 4 drawn per serial, shuffled with
global choice shuffling; two questions demonstrate per-question overrides
(``shuffle_choices: false`` and ``fixed_last: true``):

.. literalinclude:: ../../../examples/compound_exam/multiple_choice_questions.yaml
    :language: yaml
