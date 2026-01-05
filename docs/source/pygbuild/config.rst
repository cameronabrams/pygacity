.. _config:

Configuration File
------------------

``pygacity build`` requires the user to supply a configuration file describing the document(s) to be built.
This file must be in YAML format, and can be named anything.

``pygacity`` expects exactly two top-level sections in the configuration file:

- ``document``: Describes the document to be built, including its structure and content.
- ``build``: Describes how the document is to be built, including options for LaTeX compilation.

Each of these sections is described in detail below.

.. toctree::
   :maxdepth: 2

   ./config/document.rst
   ./config/build.rst