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

``serials``, ``serial-digits``, ``serial-range``, ``serial-file``, and ``serial-hex``
--------------------------------------------------------------------------------------

When ``copies`` is greater than 1 (or not specified so that it defaults to 1), ``pygacity`` uses serial numbers to differentiate multiple copies of a document when generating randomized content.  The following attributes control the generation of serial numbers:

- ``serials``: A list of integers specifying the serial numbers to be used.  If this attribute is provided, it overrides the other three serial-related attributes.
- ``serial-range``: A list of two integers specifying the inclusive range of serial numbers to be used.  For example, ``[1, 10]`` would generate serial numbers from 1 to 10.
- ``serial-digits``: An integer specifying the number of decimal digits in randomly generated serial numbers (default: ``8``).  The serial is drawn uniformly from the range ``[10^(n-1), 10^n - 1]`` where *n* is ``serial-digits``.
- ``serial-file``: A string specifying the path to a text file containing a list of serial numbers, one per line.  If this attribute is provided, it overrides the other serial-generation attributes.
- ``serial-hex``: A boolean (default: ``false``).  When ``true``, the serial number is displayed and used in output filenames as a lowercase hexadecimal string (e.g. ``1ad3e52``) rather than as a decimal integer.  The underlying integer is unchanged, so reproducibility of randomized content is fully preserved — only the visual representation differs.  For example, a serial of ``28114514`` would appear as ``1ad3e52`` in filenames and in the document header.

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