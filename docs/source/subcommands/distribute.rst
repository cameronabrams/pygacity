.. _distribute:

Distributing Exams to Students
-------------------------------

``pygacity distribute`` assigns built exam PDFs to students round-robin,
creates a per-student output folder for each, and optionally emails each
student their exam via Outlook.

.. code-block:: bash

    $ pygacity distribute <build_dir> <gradebook> [options]

Required Arguments
~~~~~~~~~~~~~~~~~~

``build_dir``
    Directory containing the built exam PDFs produced by ``pygacity build``.
    The command expects files named ``<jobname>-<serial>.pdf`` and, if present,
    solution files named ``<jobname>_soln-<serial>.pdf``.

``gradebook``
    Path to a Blackboard Learn gradebook CSV.  The file must contain at least
    the columns ``Last Name``, ``First Name``, and ``Username``.

Optional Arguments
~~~~~~~~~~~~~~~~~~

``-o`` / ``--output-dir`` (default: ``distributed/``)
    Root directory where per-student subfolders are created.  Each subfolder
    is named ``<Last Name>, <First Name>``.

``-fc`` / ``--filter-column``
    Name of a gradebook column whose value is ``yes`` or ``true`` (case-insensitive)
    for students who should receive an exam.  Rows with any other value are skipped.
    Useful when not every student in the gradebook is sitting the exam.

``--email`` / ``--no-email`` (default: off)
    Send each student their exam as an email attachment via Outlook COM
    automation.  Requires Windows and a running Outlook installation.
    Email addresses are formed as ``<Username><email-suffix>``.

``--email-suffix`` (default: ``@drexel.edu``)
    Domain suffix appended to each student's ``Username`` to form their email
    address.

``--subject`` (default: ``Your exam``)
    Subject line for outgoing emails.

``--body``
    Plain-text body for outgoing emails.

``--dry-run`` / ``--no-dry-run`` (default: off)
    Preview email actions — prints the recipient address and attachment names
    for each student without actually sending anything.  Useful for verifying
    the assignment before committing.

``--include-solutions`` / ``--no-include-solutions`` (default: on)
    Include solution PDFs in per-student folders and email attachments.
    Pass ``--no-include-solutions`` to distribute exam PDFs only.

How It Works
~~~~~~~~~~~~

1. **Discover exams** — scans ``build_dir`` for files matching
   ``<jobname>-<serial>.pdf`` and pairs each with its solution
   ``<jobname>_soln-<serial>.pdf`` if one exists.

2. **Read gradebook** — loads the Blackboard CSV, drops unnamed columns,
   optionally applies ``--filter-column``, and sorts students alphabetically
   by last name then first name.

3. **Assign versions** — iterates through the sorted student list and assigns
   exam serials round-robin (student 0 → serial 0, student 1 → serial 1, …,
   wrapping back to serial 0 after the last version).

4. **Copy files** — creates ``<output_dir>/<Last Name>, <First Name>/`` for
   each student and copies their assigned exam (and solution) PDF there.

5. **Email** (optional) — sends each student their PDF(s) via Outlook.

6. **Print summary** — displays a table of student names and assigned serial
   numbers at the end.

Examples
~~~~~~~~

Basic distribution into the default ``distributed/`` folder:

.. code-block:: bash

    $ pygacity distribute build/ gradebook.csv

Write output to a custom folder and omit solutions:

.. code-block:: bash

    $ pygacity distribute build/ gradebook.csv -o spring2026 --no-include-solutions

Only distribute to students where the ``Section A`` column is ``yes``:

.. code-block:: bash

    $ pygacity distribute build/ gradebook.csv -fc "Section A"

Preview emails without sending (dry run):

.. code-block:: bash

    $ pygacity distribute build/ gradebook.csv --email --dry-run

Send exams via Outlook with a custom subject and domain:

.. code-block:: bash

    $ pygacity distribute build/ gradebook.csv \
        --email \
        --email-suffix @university.edu \
        --subject "CHME 310 Midterm"
