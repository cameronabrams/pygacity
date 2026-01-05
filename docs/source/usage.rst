.. _usage:

Usage
-----

Building Documents
++++++++++++++++++

``pygacity build`` is the main way pygacity is used.  In general, standard use involves two major tasks:

1. Creating a configuration file describing the document to be built and how to build it.
2. Running the ``pygacity build`` command with the configuration file as input.

.. toctree::
   :maxdepth: 2

   Input Configuration Files <pygbuild/config>
   Document Compilation <pygbuild/after-build>


Generating Pygacity-Compatible LaTeX Code
+++++++++++++++++++++++++++++++++++++++

The majority of work in creating a document with ``pygacity`` is in creating pygacity-compatible LaTeX code for problems, exercises, and other types of document content.  The following sections provide guidance on these tasks.

.. toctree::
   :maxdepth: 2

   Writing LaTeX/Pythontex Problems <pygbuild/numericals>
   Python Resources Available in Pygacity <pygbuild/pythonutils>
   Short-Answer/Multiple-Choice/Fill-in-the-Blank/True-False Questions <pygbuild/shorts>

Other Subcommands
+++++++++++++++++

``pygacity`` also has three other subcommands:

.. toctree:: 
   :maxdepth: 2

   subcommands/singlet
   subcommands/answerset
   subcommands/combine
