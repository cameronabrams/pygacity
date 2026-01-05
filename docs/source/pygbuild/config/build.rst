.. _pygbuild_config_build:

``build`` subsection
======================

The ``build`` section of the configuration file describes how the document is to be built, including options for LaTeX compilation.  Four main attributes can be set in this section:

``seed``
---------

This is just an integer to seed the random number generator.  This is useful for ensuring reproducibility when generating documents with randomized content.

``copies``
----------------

This is an integer specifying the number of copies of the document to be generated.  This is useful for creating multiple versions of a document with different randomized content.  If not specified, this defaults to 1.

``serials``, ``serial-digits``, ``serial-range``, and ``serial-file``
---------------------------------------------------------------------

When ``copies`` is greater than 1 (or not specified so that it defaults to 1), ``pygacity`` uses serial numbers to differentiate multiple copies of a document when generating randomized content.  The following attributes control the generation of serial numbers:

- ``serials``: A list of integers specifying the serial numbers to be used.  If this attribute is provided, it overrides the other three serial-related attributes.
- ``serial-range``: A list of two integers specifying the inclusive range of serial numbers to be used.  For example, ``[1, 10]`` would generate serial numbers from 1 to 10.
- ``serial-digits``: An integer specifying the number of digits to use for serial numbers.  Serial numbers will be zero-padded to this length.  For example, if ``serial-digits`` is set to 3, serial number 5 would be represented as ``005``.
- ``serial-file``: A string specifying the path to a text file containing a list of serial numbers, one per line.  If this attribute is provided, it overrides the other three serial-related attributes.

If none of these attributes are specified, or if ``copies`` is set to 1, no serial numbers will be used.

``solutions``
----------------

This is a boolean value (``true`` or ``false``) indicating whether a companion document that includes full solutions (if you wrote them!).  It is ``true`` by default.

``job-name``
----------------

This is a string specifying the job name to be used in the LaTeX compilation process.  This determines the names of auxiliary files generated during compilation.

``paths``
----------------

Specific names of subdirectories to be used for various build artifacts can be set in this subsection.  The following paths can be specified:

- ``build-dir``: Directory where intermediate build files are stored; defaults to ``build/``.
- ``cache-dir``: Directory where cached files are stored; defaults to ``.cache`` under the build directory.

If any of these attributes are not specified, or the ``paths`` subsection is not provided, default values will be used.