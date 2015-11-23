.. pybraincompare documentation master file, created by
   sphinx-quickstart on Wed Oct 21 17:20:11 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Pybraincompare
==============

Semantic and computational comparison methods for brain imaging data, and visualization of outputs. Modules include:

compare
-------
An example scatterplot image comparison, dynamically rendered using python and d3 from two raw statstical brain maps and an atlas image, [is available](http://vbmis.com/bmi/share/neurovault/scatter_atlas.html). A new addition (beta) is a [canvas based scatterplot](http://vbmis.com/bmi/project/brainatlas) that can render 150K + points.

ontology
--------
This module will let you convert a triples data structure defining relationships in an ontology to a an interactive d3 visualization, demo is [is available](http://vbmis.com/bmi/share/neurovault/ontology_tree.html). Reverse inference tree also [in development](http://vbmis.com/bmi/share/neurovault/reverse_inference.html).

network
-------
This module will work with visualization of functional connectivity data, demo is [is available](http://vbmis.com/bmi/share/neurovault/connectogram.html) and see examples folder for how to run with your data.

QA for Statistical Maps 
-----------------------
This module will generate a web report for a list of statistical maps, demo [is available](http://www.vbmis.com/bmi/project/qa/index.html). Much work to be done! Please submit an issue if you have feedback.

histogram
---------
An example histogram using python and chartJS from a single brain map [is available](http://vbmis.com/bmi/share/neurovault/histogram.html).

This package is maintained by Vanessa Sochat at Stanford University, proud member of Poldracklab. Pybraincompare drives image comparison in `NeuroVault <http://www.neurovault.org>`_ and `published methods <http://journal.frontiersin.org/article/10.3389/fnins.2015.00418/abstract>`_ have also been included. Please submit bugs and feature requests on the `Github Repo <https://github.com/vsoch/pybraincompare>`_.

Contents:

.. toctree::
   :maxdepth: 2

   installation
   spatial_image_comparison
   semantic_image_comparison
   additional_tools
   modules
   GitHub repository <https://github.com/vsoch/pybraincompare>


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
