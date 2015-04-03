#pybraincompare
<!---
Dev environment not possible to setup without sudo access
![build_status](https://travis-ci.org/vsoch/pybraincompare.svg?branch=master)
[![Coverage Status](https://coveralls.io/repos/vsoch/pybraincompare/badge.svg)](https://coveralls.io/r/vsoch/pybraincompare)
-->

Comparison and Visualization Methods for Brains in Python, using d3

UNDER DEVELOPMENT

## Installation

#### manual Installation

     git clone https://github.com/vsoch/pybraincompare
     cd pybraincompare
     sudo python setup.py install

#### pip Installation

     pip install pybraincompare


### compare
An example scatterplot image comparison, dynamically rendered using python and d3 from two raw statstical brain maps and an atlas image, [is available](http://vbmis.com/bmi/share/neurovault/scatter_atlas.html)

### annotate
This module will let you convert a triples data structure defining relationships in an ontology to a an interactive d3 visualization, demo is [is available](http://vbmis.com/bmi/share/neurovault/ontology_tree.html). Reverse inference tree also [in development](http://vbmis.com/bmi/share/neurovault/reverse_inference.html).

### network
This module will work with visualization of functional connectivity data, demo is [is available](http://vbmis.com/bmi/share/neurovault/connectogram.html) and see examples folder for how to run with your data.

### QA for Statistical Maps 
This module will generate a web report for a list of statistical maps, demo [is available](http://www.vbmis.com/bmi/project/qa/index.html). Much work to be done! Please submit an issue if you have feedback.
