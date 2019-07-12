



----------------
 A first example
----------------

Let's start with a simple point defined by 2 coordinates: `x` and `y`.

A simple python `Point` type and its possible representation in yaml are:

.. code:: python

  from collections import namedtuple

  mkPoint = namedtuple('Point', 'x y')

  doc = """
      x: 2
      y: 5
      """

The goal is to read this yaml doc and build a corresponding python Point value.

The first step is to define a decoder for the `Point` type. Such a decoder is a python type which knows two things:

- the expected structure of the yaml document.
- how to create a `Point`.

Once this is done, we can then use `parse_yaml()` to apply the decoder to the yaml document and return the value produced by the decoder.

.. code:: python

  from jazzml import *

  point_decoder = mapn(mkPoint, field('x', Int), field('y', Int))

  point = parse_yaml(doc, point_decoder)



`field('x', Int)` looks for a field named `x`. If the field exists then it checks the type of its value. If the value is an `int`, it returns it.

If the field does not exist or its value is not an int, the parser fails.

.. code:: python

  mapn(func, decoder_1, decoder_2, ..., decoder_n)

The 'mapn()' function creates a new decoder which does 3 things:

- it sequentially applies decoders 1 to n and collects the value each decoder produces.
- it then calls the function `func` with the decoder values as arguments.
- it produces the value returned by the call to `func`.

So, the type of the value produced by the decoder created by `mapn(func, ...)` is the return type of `func`.

If any given decoder fails, the decoder returned by `mapn()` fails as well.


So looking again at our point decoder:

.. code:: python

  point_decoder = mapn(mkPoint, field('x', Int), field('y', Int))

It looks into the yaml document for an integer field named `x`, then for an integer field named `y`. If these fields exist and contain integers, it calls the constructor `mkPoint`.


It is important to note that the function `func` given to  `mapn()` does not have to be a constructor. It can be any function which takes as many arguments as the number of given decoders.

For instance, we could write a decoder that sums the fields `x` and `y`.

.. code:: python

  sum_decoder = mapn(lambda a, b: a+b, field('x', Int), field('y', Int))

  parse_yaml(doc, sum_decoder) == 7  # True


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

  circle = parse_yaml(doc, circle_decoder)

`circle_decoder` follows the same logic as our previous `point_decoder`.

It looks for a field named `centre` and tries to decode its value using `point_decoder`.
Thus, it expects the field `centre` to contain a composite value of type `Point`.

This example shows how decoders can be composed into much larger and arbitrarily complex decoders.


------------------------
 Decoding pimitive types
------------------------

`jazzml` define built-in decoders for yaml primitive types: `Int`, `Float`, `String`, `Bool`.


.. code:: python

  parse_yaml('1', Int) == 1
  parse_yaml('1.2', Float) == 1.2
  parse_yaml('True', Bool) == True
  parse_yaml('Hello World', Str) == 'Hello World'

In addition, the built-in decoder `Real` decodes a value that is either a integer or a float.

.. code:: python

  parse_yaml('1', Real) == 1      # int python type
  parse_yaml('1.2', Real) == 1.2  # float python type


The las built-in decoder is `null()` which decode a yaml null value into a specified
python value.

.. code:: python

  parse_yaml('', null()) == None
  parse_yaml('', null(42)) == 42
  parse_yaml('a:', field('a', null(True))) == True





----------------
 Decoding a list
----------------


If the yaml document contains a list of `Point`, we can build a corresponding list decoder:

.. code:: python

  points_decoder = List(point_decoder)

  doc = """
      - x: 1
        y: 2
      - x: 10
        y: 20
    """

  points = parse_yaml(doc, points_decoder)


---------------------------
 Decoding an optional field
---------------------------

Let's consider a colored point having ef 3 attributes `x`, `y` and `color`.

Attributes `x` and `y` are mandatory but `color` is optional. If the yaml doc does not contain it, the decoder will set it to `None`or to a default value defined by the user.

.. code:: python


  from collections import namedtuple

  from jazzml import *

  mkColoredPoint = namedtuple('ColoredPoint', 'x y color')

  doc_color = """
       x: 2
       y: 5
       color: 'red'
       """

  doc_no_color = """
       x: 2
       y: 5
       """

  colored_point_decoder = mapn(mkColoredPoint, field('x', Int), field('y', Int),  \
    optional_field('color', Str))

  colored_point = parse_yaml(doc_color, colored_point_decoder)
  non_colored_point = parse_yaml(doc_no_color, colored_point_decoder)

It is possible to specify a default value in case the field is missing:

.. code:: python

  colored_point_decoder = mapn(mkColoredPoint, field('x', Int), field('y', Int),  \
    optional_field('color', Str, default='black'))


-----------------------------------------
 Choosing between various representations
-----------------------------------------

Suppose we have a Shape hierarchy with Circles and Polygon as subclasses:

.. code:: python

  class Shape:
      pass

  class Circle(Shape):

      def __init__(self, centre, radius):
          self.centre = centre
          self.radius = radius

  class Polygon(Shape):

      def __init__(self, vertices):
          self.vertices = vertices

  circle_decoder = mapn(Circle, field('centre', point_decoder), field('radius', Int))

  polygon_decoder = mapn(Polygon, field('points', List(point_decoder)))

  doc_circle = """
      centre:
          x: 1
          y: 2
      radius: 20
      """

  doc_polygon = """
    points:
      - x: 1
        y: 2
      - x: 3
        y: 6
      - x: 1
        y: 3
      """

  shape_decoder = one_of([circle_decoder, polygon_decoder])

  parse_yaml(doc_circle, shape_decoder) # a Circle
  parse_yaml(doc_polygon, shape_decoder) # a Polygon


`one_of([decoder_1, decoder_2, ..., decoder_n])` creates a decoder that sequentially applies each decoder in the given list until one of them succeeds.

If all decoders fail, then the decoding fails.

Decoding a list of Shapes is straightforward:

.. code:: python

  doc_shapes = '''
    - centre:
         x: 1
         y: 2
      radius: 20

    - points:
          - x: 1
            y: 2
          - x: 3
            y: 6
          - x: 1
            y: 3
    - centre:
         x: 10
         y: 22
      radius: 20
    - points:
          - x: 0
            y: -1
          - x: 2
            y: 7
        '''

  shapes_decoder = List(shape_decoder)

  parse_yaml(doc_shapes, shapes_decoder)  # list of Shapes



The next example shows how we can decode an integer (if present) or return a specific value if a null is encountered.

.. code:: python

  decoder = field('a', one_of([Int, null(42)]))

  parse_yaml('a: 56', decoder) == 56
  parse_yaml('a: ', decoder) == 42


------------------------------------
 Other interesting built-in decoders
------------------------------------

`succeed()` creates a decoder which always succeeds and produces a given value, whatever the document.


.. code:: python

  decoder = succeed("your value")

  doc = """
      a:1
      b: "anything"
      """

  parse_yaml(doc, decoder) == "your value"


`fail()` creates a decoder which always fails.

.. code:: python

  decoder = fail("your error message")

  doc = """
      a:1
      b: "anything"
      """

  parse_yaml(doc, decoder) == "your value"



`nullable(decoder, default = value)` first looks at the document. If the document is not null, it applies the given decoder otherwise it returns the a defaut value.

.. code:: python

  parse_yaml('', nullable(Int)) == None

  parse_yaml('', nullable(Int, 42)) == 42

  parse_yaml('a: 6', field('a', nullable(Int, 42))) == 6

  parse_yaml('a: ', field('a', nullable(Int, 42))) == 42

  parse_yaml('a: true', field('a', nullable(Int, 42)))  # error: Bad Type


------------------------------------
 Decoding recursive data structures
------------------------------------

Creating a decoder for recursive data structure can be done with `lazy()`.

The argument to `lazy()` must be a function which takes no argument and returns a decoder.

Consider the following yaml document which represents a linked list. Each node of the list contains a value (head) and a representation of the next node (tail).

The last item of the list is a node whose tail is `None`.

.. code:: python

  doc = """
      head: 1
      tail:
       head: 2
       tail: null
      """

  mkCons = namedtuple('Cons', 'head tail')


A first attempt to create a Decoder could be:

.. code:: python

  node_decoder = return mapn(mkCons, field('head', Int), field('tail', nullable(node_decoder)))

And python will complain that `list_decoder` is used before being defined.

Another approach is to create a little factory for our decoder and passing it to `lazy()`.

.. code:: python

  def mk_node_decoder() : return mapn(mkCons, field('head', Int), field('tail', nullable(lazy(mk_node_decoder))))

  node_decoder = mk_node_decoder()

  parse_yaml(doc, node_decoder) # Cons(h=1, t=Cons(h=2, t=None))


------------------------------------
 Dynamic selection of Decoders
------------------------------------

In some cases, while the document is being decoded, it might be useful to select the next decoder to apply based on an already decoded value.

For that, you can use the `then()` method.

If we have a document which contains versioned data, a possible solution is:

.. code:: python

  doc = """
      - version: 1
        a: 6
      - version: 2
        b: "Good morning"
      """


  def mkVersionedDecoder(version):
      if version == 1:
          return field( 'a', Int)
      elif version == 2:
          return field('b', Str)
      else:
          return fail("Bad version")


  decoder = field('version', Int).then(mkVersionedDecoder)

  parse_yaml(doc, List(decoder)) == [6, "Good morning"]

------------------------------------
 Another way to compose decoders
------------------------------------

For those who find `mapn()` syntax too heavy, it can be replaced by two infix operators: `*` and `@`.

.. code:: python

  from collections import namedtuple

  mkPoint = namedtuple('Point', 'x y')

  mkCircle = namedtuple('Circle', 'centre radius')

  doc = """
      centre:
          x: 2
          y: 5
      radius: 10
      """

  point_decoder = succeed(mkPoint) * field('x', Int) @ field('y', Int)

  circle_decoder = succeed(mkCircle) * field("centre", point_decoder) @ field("radius", Int)

  circle = parse_yaml(doc, circle_decoder)







