.. jazzml documentation master file, created by
   sphinx-quickstart on Mon Jul  1 22:48:47 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to jazzml!
==================

`jazzml` is a lightweight package to decode both json and yaml documents.

It does so by allowing the user to first specify a Decoder and then apply it to a json/yaml document.

A Decoder can be viewed as a specification of the expected structure of a json/yaml document.

This 2 step strategy brings some level of implicit checking. That is, if a document structure does not conform to the Decoder, the parsing will fails.

Other nice features of `jazzml` includes the possibility to define Decoders for recursive data structures and to dynamically chose a Decoder based on some specific value defined by the json/yaml document.

I hope you'll enjoy it.


.. toctree::
   :maxdepth: 2
   :caption: Contents:
   :hidden:

   guide
   api







