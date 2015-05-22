#!/usr/bin/python

"""
Test transformation functions
"""
from pybraincompare.mr.transformation import make_resampled_transformation_vector, make_resampled_transformation
from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from nose.tools import assert_true, assert_false
import nibabel
import random
import pandas
import numpy
import os

def test_masked_transformation():


def test_unmasked_transformation():


  # Get standard brain mask
  mr_directory = get_data_directory()
  standard = "%s/MNI152_T1_2mm_brain_mask.nii.gz" %(mr_directory)
  thresholds = [0.0,0.5,1.0,1.5,1.96,2.0]

  # Generate random data inside brain mask, run 10 iterations
  standard = nibabel.load(standard)
  number_values = len(numpy.where(standard.get_data()!=0)[0])
  numpy.random.seed(9191986)
  for x in range(0,10):  
    data1 = norm.rvs(size=number_values)
    data2 = norm.rvs(size=number_values)
    corr = pearsonr(data1,data2)[0]
      
    # Put into faux nifti images
    mr1 = numpy.zeros(standard.shape)
    mr1[standard.get_data()!=0] = data1
    mr1 = nibabel.nifti1.Nifti1Image(mr1,affine=standard.get_affine(),header=standard.get_header())
    mr2 = numpy.zeros(standard.shape)
    mr2[standard.get_data()!=0] = data2
    mr2 = nibabel.nifti1.Nifti1Image(mr2,affine=standard.get_affine(),header=standard.get_header())  
    pdmask = make_binary_deletion_mask([mr1,mr2])
    pdmask = nibabel.Nifti1Image(pdmask,header=mr1.get_header(),affine=mr1.get_affine())
    score = calculate_correlation(images = [mr1,mr2],mask=pdmask)  
    assert_almost_equal(corr,score,decimal=5)
