.. _numericals:

Writing Numerical Problems in Pygacity
--------------------------------------

Here is a very short example of a numerical problem, first in LaTeX form:

.. code-block:: latex

  A circle has area $A$ = 0.25 cm$^2$.  What is its radius?

Suppose that represents the entire contents of the file ``radius.tex``.  One might imagine including it in an enumerated list 
in, for example, ``exam.tex`` like so:

.. code-block:: latex

    (...other items...)
    \item \input{radius}
    (...more items...)

How would we modify ``radius.tex`` for pygacity?  Very simply:

.. code-block:: latex

    \begin{pycode}
    from math import pi, sqrt
    A = 0.25 # cm
    # A = pi * r**2 ==> r = sqrt(A/pi)
    r = sqrt(A/pi)
    AnsSet.register(1, label=r'\(r\) (cm)', value = r)
    \end{pycode}
    A circle has area $A$ = \py{A} cm$^2$.  What is its radius?

    \ifshowsolutions
    Solution: Since area $A$ and radius $r$ of a circle are related by
    \[
        A = \pi r^2
    \]
    we know that
    \[
        r = \sqrt{\frac{A}{\pi}}
    \]
    Using the value of area provided:

    \begin{align*}
    r & = \sqrt{\frac{\py{A}}{\py{f'{pi:.4f}'}}}\\
      & = \py{f'{r:.2f}'}\ \mbox{cm.}
    \end{align*}

    \fi

First, we used a single ``pycode`` block to solve the problem in Python.  Then, we *reference* the required numerical values using ``py`` directives in the LaTeX code.  Finally, using pygacity's ``\ifshowsolutions`` conditional, we include a short solution statement.

Now this is quite a bit larger than the original ``radius.tex``, but look at all the new stuff it provides.  There is only one place where the input value of area needs to be set: in the ``pycode`` block.  Also, in the solution set that accompanies the assignment, the full solution provided in this new ``radius.tex`` is provided.

Following this basic pattern, there is nearly an infinite variety of numerical problems that pygacity can typeset for you.