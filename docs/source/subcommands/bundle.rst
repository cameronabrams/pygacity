.. _bundle:

Creating Bundled PDFs
----------------------

The ``bundle`` subcommand combines student exam PDFs from an existing build directory
into one or more print-ready bundle PDFs.  It is useful when the ``--bundle-size`` option
was not passed to ``pygacity build``, or when you want to re-bundle with different
settings after the fact.

.. code-block:: bash

    pygacity bundle <build_dir> [--bundle-size N] [--two-sided]

``<build_dir>`` is the directory containing the built student exam PDFs (typically the
``build/`` subdirectory created by ``pygacity build``).

Student exam PDFs are identified automatically by excluding files whose names contain
``_soln``, ``answerset``, or ``bundle``.  They are sorted by modification time
(i.e. the order in which they were built) before being grouped.

Options
~~~~~~~

``--bundle-size N``
    Number of exams to include in each bundle PDF (default: ``10``).  If the total
    number of exams is not a multiple of *N*, the last bundle will contain the
    remainder.

``--two-sided`` / ``--no-two-sided``
    When ``--two-sided`` is set, a blank page is appended to any exam that has an
    odd number of pages before it is merged into the bundle.  This ensures that the
    first page of every exam falls on a right-hand sheet when the bundle is printed
    double-sided (default: off).

Output
~~~~~~

Bundle PDFs are written to ``<build_dir>`` alongside the individual exam files, named
``{job-name}-bundle-1.pdf``, ``{job-name}-bundle-2.pdf``, etc., where ``{job-name}``
is inferred from the stem of the first student exam PDF found.
