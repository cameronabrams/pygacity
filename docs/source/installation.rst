.. _installation:

Installation
------------

Pygacity can be installed via pip from PyPI:

.. code-block:: bash

   pip install pygacity

Alternatively, you can install Pygacity directly from the source code. First, clone the repository:

.. code-block:: bash

   git clone git@github.com:cameronabrams/pygacity.git # ssh access assumed

Then, navigate to the cloned directory and install using pip:

.. code-block:: bash

   cd pygacity
   pip install -e .  # the -e flag installs in editable mode

Pygacity uses ``pdflatex`` and ``pythontex`` to build assignments and exams. Make sure you have a working LaTeX distribution installed on your system. You can download and install `TexLive <https://www.tug.org/texlive/>`_ or `MikTex <https://miktex.org/>`_.  These will come with ``pdflatex`` an ``pythontex`` packages.