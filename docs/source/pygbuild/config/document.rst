.. _pybuild_config_document:

``document`` Section
====================

The ``document`` section of the configuration file describes the document to be built, including its structure and content.  It contains the following subsections:

- ``preamble`` (optional): This is a single string containing LaTeX code to be included in the preamble of the document.
- ``structure``: This subsection describes the hierarchical structure of the document, including chapters, sections, subsections, and so on. It is represented as a nested list of dictionaries, where each dictionary represents a document element (termed a **block**) and its content.

.. toctree::
   :maxdepth: 2

   ./document/preamble.rst
   ./document/structure.rst
