#!/usr/bin/python

"""
Test histogram output
"""
from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from pybraincompare.report.histogram import plot_histogram
from pybraincompare.mr.datasets import get_pair_images
from nose.tools import assert_true, assert_false
import re

'''Test that histogram returns same output'''
def test_histogram_output():
    image = get_pair_images()[0]
    html_snippet = plot_histogram(image,view_in_browser=False)
    html_snippet = "".join(html_snippet)

    # This is the output we should get
    expected_output = '<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/1.0.2/Chart.min.js"></script>\n\n<!-- Image Histogram-->\n<div id = "imagehistogram" class="span12 widget blue" onTablet="span11" onDesktop="span12">\n<div class="clearfix"></div><br>\n<canvas id="histogram" width="1000" height="400"></canvas>\n    <script>\n\tvar ctx = document.getElementById("histogram").getContext("2d");\n        var data = {\n    \tlabels: ["-3.68","-3.38","-3.09","-2.79","-2.49","-2.19","-1.90","-1.60","-1.30","-1.00","-0.71","-0.41","-0.11","0.19","0.48","0.78","1.08","1.38","1.67","1.97","2.27","2.57","2.86","3.16","3.46","3.76"],\n\t\twidth: 400,\n   \t \tdatasets: [\n        \t{\n            \t    label: "Image Histogram",\n            \t    fillColor: "rgba(220,220,220,0.5)",\n            \t    strokeColor: "rgba(220,220,220,0.8)",\n            \t    highlightFill: "rgba(220,220,220,0.75)",\n            \t    highlightStroke: "rgba(220,220,220,1)",\n            \t    data: ["12","61","259","628","1248","2221","3553","4935","6394","8883","13358","20249","34123","20216","14296","10137","7003","4402","2532","1245","612","230","50","16","7"]\n                }]\n\t};\n        histogram = new Chart(ctx).Bar(data, { multiTooltipTemplate: "<%= datasetLabel %> - <%= value %>", scaleFontColor: "#000"});    \t\t\t\t\t\n    </script>\n</div>\n'

    assert_equal(expected_output,html_snippet)
