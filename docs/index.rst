.. jazzml documentation master file, created by
   sphinx-quickstart on Mon Jul  1 22:48:47 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to jazzml's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


.. toctree::
  :maxdepth: 1
  :hidden:

  a
  b


----------------
 A first example
----------------

.. code:: python

  from collections import namedtuple

  mkPoint = namedtuple('Point', 'x y')

  doc = """
      x: 2
      y: 5
      """

.. code:: python

  from jazzml import *

  point_decoder = mapn(mkPoint, field('x', Int), field('y', Int))

  point = parse_yaml_string(doc, point_decoder)

.. code:: python

  x_decoder = field('x', Int)

`x_decoder` looks for a field named `x`. It the field exists then it checks the type of its value.
If the value is an `int`, it returns it.

If the field does not exist or its value is not an int, the parser fails.

.. code:: python

  mapn(func, decoder_1, decoder_2, ..., decoder_n)

The 'mapn()' function creates a new decoder which does 3 things:

- it sequentially applies decoders 1 to n and collects the value each decoder has produced.
- it then calls the function `func` with decoder values as arguments.
- it produces the value returned by the call to `func`.

So the type of the value produced by `mapn(func, ...)` is the return type of `func`.

If any given decoder fails, the decoder returned by `mapn`fails as well.


So looking again at out point decoder:

.. code:: python

  point_decoder = mapn(mkPoint, field('x', Int), field('y', Int))

It looks into the json/yaml document for an integer field named `x`, then for an integer field named `y`. If these fields exist and contain integers, it calls the constructor `mkPoint`.


It is important to note that the function `func` given to  `mapn()` does not have to be a constructor. It can be any function as long as that function takes as many arguments as the number of given decoders.

For instance, we could write a decoder that sums the fields `x` and `y`.

.. code:: python

  sum_decoder = mapn(lambda a, b: a+b, field('x', Int), field('y', Int))

  parse_yaml_string(doc, sum_decoder) == 7  # True


----------------------
 Decoding nested types
----------------------

Suppose we want to decode a value representing a circle. A circle is defined a point (its centre) and a radius.

.. code:: python

  from collections import namedtuple

  mkPoint = namedtuple('Point', 'x y')

  mkCircle = namedtuple('Circle', 'centre radius')

A yaml representation of a circle could be:

.. code:: python

  doc = """
      centre:
          x: 2
          y: 5
      radius: 10
      """

And a circle decoder would be:

.. code:: python

  circle_decoder = mapn(mkCircle, field("centre", point_decoder), field("radius", Int))

  circle = parse_yaml_string(doc, circle_decoder)

`circle_decoder` follows the same logic as our previous `point_decoder`.

It looks for a field named `centre` and tries to decode its value using the given `point_decoder`.
Thus, it expects field `centre` to contain a composite value of type `Point`.

This example shows how decoders can be composed into much larger and arbitrarily complex decoders.



Grid table:

+------------+------------+-----------+
| Header 1   | Header 2   | Header 3  |
+============+============+===========+
| body row 1 | column 2   | column 3  |
+------------+------------+-----------+
| body row 2 | Cells may span columns.|
+------------+------------+-----------+
| body row 3 | Cells may  | - Cells   |
+------------+ span rows. | - contain |
| body row 4 |            | - blocks. |
+------------+------------+-----------+

Simple table:

=====  =====  ======
   Inputs     Output
------------  ------
  A      B    A or B
=====  =====  ======
False  False  False
True   False  True
False  True   True
True   True   True
=====  =====  ======



:Authors:
    Tony J. (Tibs) Ibbs,
    David Goodger
    (and sundry other good-natured folks)

:Version: 1.0 of 2001/08/08
:Dedication: To my father.

:tomek: hhh


a      a def
b      b def
c      c def

-a            command-line option "a"
-b file       options can have arguments
              and long descriptions
--long        options can be long also
--input=file  long options can also have
              arguments
/V            DOS/VMS-style options too

================
 Document Title
================

----------
 Subtitle
----------

Section Title
=============

Chapter 1 Title
===============

Section 1.1 Title
-----------------

Section 1.1.1 Title
~~~~~~~~~~~~~~~~~~~

Section 1.2 Title
-----------------

Chapter 2 Title
===============



This is a paragraph.  It's quite
short.

   This paragraph will result in an indented block of
   text, typically used for quoting other text.

This is another one.

``double back-quotes``

An example::

    Whitespace, newlines, blank lines, and all kinds of markup
      (like *this* or \this) is preserved by literal blocks.
  Lookie here, I've dropped an indentation level
  (but not far enough)
   no more example

 no more example



=====

what
  Definition lists associate a term with a definition.

*how*
  The term is a one-line phrase, and the definition is one or more
  paragraphs or body elements, indented relative to the term.
  Blank lines are not allowed between term and definition.


aaa
  eee

1. numbers

   dde

  dede

   - jjj

A. upper-case letters
   and it goes over many lines

   with two paragraphs and all!

a. lower-case letters

   3. with a sub-list starting at a different number

   2. make sure the numbers are in the correct sequence though!

I. upper-case roman numerals

i. lower-case roman numerals

(1) numbers again

1) and again



`Section 1.1 Title`_


$project
========

$project will solve your problem of where to start with documentation,
by providing a basic explanation of how to do it easily.

Look how easy it is to use:

    import project
    # Get your stuff done
    project.do_stuff()

Features
--------

- Be awesome
- Make things faster

Installation
------------

Install $project by running:

    install project

Contribute
----------

- Issue Tracker: github.com/$project/$project/issues
- Source Code: github.com/$project/$project

Support
-------

If you are having issues, please let us know.
We have a mailing list located at: project@google-groups.com

License
-------

The project is licensed under the BSD license.


:mod:`pyendeavor` Package
-------------------------

.. automodule:: jazzml
    :members:
