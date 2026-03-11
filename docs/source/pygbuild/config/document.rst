.. _pybuild_config_document:

``document`` Section
====================

The ``document`` section of the configuration file describes the document to be built, including its structure and content.  It contains the following subsections:

- ``preamble`` (optional): Controls the LaTeX preamble injected before ``\begin{document}``.  Accepts a literal LaTeX string, ``null`` (to apply built-in defaults), or a structured dict with ``font``, ``pagestyle``, and ``commands`` sub-keys.
- ``structure``: An ordered list of **blocks** that defines the document body.  Each block is a dict whose key determines the block type (``source``, ``text``, ``pythontex``, or question block).

.. toctree::
   :maxdepth: 2

   ./document/preamble.rst
   ./document/structure.rst
