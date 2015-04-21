#!/usr/bin/python

"""
Test scatterplot compare output
"""
from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from pybraincompare.mr.datasets import get_data_directory
from pybraincompare.compare.scatterplot import scatterplot_compare
from nose.tools import assert_true, assert_false
from scipy.stats import norm
import nibabel
import random
import numpy
import re

# https://github.com/NeuroVault/NeuroVault/issues/133#issuecomment-74464393
# This test works locally, does not work on Travis. Removed from run_tests
'''Test that scatterplot compare returns error message for the following cases:
Case 1: no overlap in the images
Case 2: fewer than three surviving values for all regions
'''
def test_scatterplot_error_message():

  # Get standard brain mask
  mr_directory = get_data_directory()
  standard = "%s/MNI152_T1_8mm_brain_mask.nii.gz" %(mr_directory)
  standard = nibabel.load(standard)
  unzip = lambda l:tuple(zip(*l))

  # This is the error message we should see
  error = re.compile('Scatterplot Comparison Correlations Not Possible')

  # Case 1: provided pdmask masks all voxels (eg, no overlap in images) 
  data1 = norm.rvs(size=500)
  data2 = norm.rvs(size=500)  
  image1 = numpy.zeros(standard.shape)
  image2 = numpy.zeros(standard.shape)
  x,y,z = numpy.where(standard.get_data()==1)
  idx = zip(x,y,z)
  image1_voxels = unzip(idx[0:500])
  image2_voxels = unzip(idx[1500:2000])
  image1[image1_voxels] = data1
  image2[image2_voxels] = data2
  image1 = nibabel.nifti1.Nifti1Image(image1,affine=standard.get_affine(),header=standard.get_header())  
  image2 = nibabel.nifti1.Nifti1Image(image2,affine=standard.get_affine(),header=standard.get_header())  
  html_snippet,data_table = scatterplot_compare(images=[image1,image2],
                                                        reference = standard,
                                                        image_names=["image 1","image 2"],
                                                        corr_type="pearson")
  html_snippet = " ".join(html_snippet)
  assert_true(bool(error.search(html_snippet)))

  # Case 2: fewer than 3 voxels overlapping
  data1 = norm.rvs(size=2)
  data2 = norm.rvs(size=2)  
  image1 = numpy.zeros(standard.shape)
  image2 = numpy.zeros(standard.shape)
  x,y,z = numpy.where(standard.get_data()==1)
  idx = zip(x,y,z)
  idx = unzip(idx[10:12])
  image1[idx] = data1
  image2[idx] = data2
  image1 = nibabel.nifti1.Nifti1Image(image1,affine=standard.get_affine(),header=standard.get_header())  
  image2 = nibabel.nifti1.Nifti1Image(image2,affine=standard.get_affine(),header=standard.get_header())  
  html_snippet,data_table = scatterplot_compare(images=[image1,image2],
                                                        reference = standard,
                                                        image_names=["image 1","image 2"],
                                                        corr_type="pearson")
  html_snippet = " ".join(html_snippet)
  assert_true(bool(error.search(html_snippet)))

  # Case 2: But 3 should work
  data1 = norm.rvs(size=3)
  data2 = norm.rvs(size=3)  
  image1 = numpy.zeros(standard.shape)
  image2 = numpy.zeros(standard.shape)
  x,y,z = numpy.where(standard.get_data()==1)
  idx = zip(x,y,z)
  idx = unzip(idx[10:13])
  image1[idx] = data1
  image2[idx] = data2
  image1 = nibabel.nifti1.Nifti1Image(image1,affine=standard.get_affine(),header=standard.get_header())  
  image2 = nibabel.nifti1.Nifti1Image(image2,affine=standard.get_affine(),header=standard.get_header())  
  html_snippet,data_table = scatterplot_compare(images=[image1,image2],
                                                        reference = standard,
                                                        image_names=["image 1","image 2"],
                                                        corr_type="pearson")
  html_snippet = " ".join(html_snippet)
  assert_false(bool(error.search(html_snippet)))
