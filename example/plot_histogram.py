#!/usr/bin/python

from pybraincompare.report.histogram import plot_histogram
from pybraincompare.mr.datasets import get_pair_images

image = get_pair_images()[0]
plot_histogram(image)
