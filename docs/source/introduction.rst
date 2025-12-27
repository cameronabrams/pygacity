Introduction
------------

What is Pygacity?
+++++++++++++++++

Having taught engineering courses at the university level for over twenty years now, I've enjoyed making nice-looking exams and assignment documents using LaTeX.  Typesetting numerical solutions, however, can be a real drag.  Pygacity started with me using Pythontex to "solve" problems while the documents are being built, and then grew into a versatile application for generation of a variety of assignment and exams.  If you are familiar with using LaTeX to generate documents, and are comfortable with Python for numerical problem-solving, Pygacity is a useful tool for you.

Why Use Pygacity?
+++++++++++++++++

Pygacity simplifies the generation of assignment and exam documents, but it also facilitates *versioning* of these documents.  You can make any number of unique versions of a given exam, each of which has a unique set of, for example, initial conditions for numerical problems--and therefore, unique solutions.  The benefits of such a capability are obvious from an academic integrity standpoint.  Pygacity also facilitates mixing in short-answer, fill-in-the-blank, multiple-choice, and true/false questions, all of which can be provided in the form of simple YAML files.  Because a user programs the solution for every computational problem in Python, the user can also use anything available in Python to solve a problem or provide input data to a problem.  Pygacity also builds custom solution sets and solution summaries for all such versioned documents to ease grading.

How Easy is Pygacity to Use?
++++++++++++++++++++++++++++

If you are already used to LaTeX and Python, you should find it pretty easy to use Pygacity.  At its most simplistic, generating an assignment or exam document requires the following steps:

1. For each numerical problem you want to include:
   a. Write/generate Python code that solves the problem.
   b. Generate Latex code for that can be imported after an ``\item`` directive for each problem.  The ``tex`` file containing this code should begin with a ``\begin{pycode}`` block that contains the Python code.  Within the text of the problem (and its solution), you can include references to numerical values using ``\py{}`` directives.  
2. To include short-answer, fill-in-the-blank, multiple-choice, and/or true/false questions, generate one or more YAML files containing question databases.
3. Generate a YAML-format configuration file describing the structure of the document.
4. Run pygacity like this: ``pygacity build <myfile>.yaml``

