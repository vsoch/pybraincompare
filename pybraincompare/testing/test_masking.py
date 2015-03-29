#!/usr/bin/python

"""
Test that pairwise deletion mask (intersection) returns expected values
"""
from pybraincompare.mr.datasets import get_pair_images, get_data_directory
from pybraincompare.compare.mrutils import make_binary_deletion_mask, make_binary_deletion_vector
from pybraincompare.mr.datasets import get_data_directory
from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from nose.tools import assert_true, assert_false
from nilearn.image import resample_img
import nibabel
import random
import pandas
import numpy
import os

'''Test that binary deletion mask returns expected overlap given two images, nans and zeros'''
def test_binary_deletion_mask():

  mr_directory = get_data_directory()
  standard = "%s/MNI152_T1_8mm_brain_mask.nii.gz" %(mr_directory)
  brain_mask = nibabel.load(standard) 
  unzip = lambda l:tuple(zip(*l))
  
  # We will generate data with the following overlap percentages
  overlap_percents = [0.0,0.25,0.5,0.75,1.0]
  for overlap in overlap_percents:
    image1 = numpy.zeros(brain_mask.shape)
    image2 = numpy.zeros(brain_mask.shape)
    x,y,z = numpy.where(brain_mask.get_data()==1)
    idx = zip(x,y,z)
    numpy.random.shuffle(idx) 
    number_voxels = len(idx)
    number_overlap_voxels = int(numpy.floor(overlap*number_voxels))
    remaining_voxels = int(number_voxels - number_overlap_voxels)
    # We break the remaining voxels into 4 groups:
    # - nans that will overlap
    # - zeros that will overlap (no change to images here, already zeros)
    # - nans in image1, random sample of values in image2
    # - zeros in image2, random sample of values in image1 
    group_size = remaining_voxels/4
    if overlap != 0.0:
      # Here are the overlapping voxels for each image
      overlap_idx = unzip(idx[0:number_overlap_voxels])
      image1[overlap_idx] = 1
      image2[overlap_idx] = 1 
    if overlap != 1.0: 
      # Nans that will overlap
      nans_overlap_idx = unzip(idx[number_overlap_voxels:(number_overlap_voxels+group_size)])
      image1[nans_overlap_idx] = numpy.nan
      image2[nans_overlap_idx] = numpy.nan
      # Nans in image1, random sample of values in image 2
      start = number_overlap_voxels+group_size
      end = number_overlap_voxels+2*group_size
      nans_image1 = idx[start:end]
      values_image2 = unzip(random.sample(nans_image1,int(group_size/2)))
      image1[unzip(nans_image1)] = numpy.nan
      image2[values_image2] = 0.5
      # Zeros in image2, random sample of values in image 1
      start = number_overlap_voxels+2*group_size
      end = number_overlap_voxels+3*group_size
      zeros_image2 = idx[start:end]
      values_image1 = unzip(random.sample(zeros_image2,int(group_size/2)))
      image1[values_image1] = 0.75
    # Create nifti images and pdmask
    nii1 = nibabel.Nifti1Image(image1,affine=brain_mask.get_affine(),header=brain_mask.get_header())
    nii2 = nibabel.Nifti1Image(image2,affine=brain_mask.get_affine(),header=brain_mask.get_header())
    pdmask = make_binary_deletion_mask([nii1,nii2]) 
    actual_overlap = len(numpy.where(pdmask!=0)[0])
    print "Overlap %s percent: should have %s, actual %s" %(overlap,number_overlap_voxels,actual_overlap)
    assert_equal(actual_overlap,number_overlap_voxels)

'''Test that returned image is binary, no nans, infs'''
def test_binary_deletion_mask_values():
   
  images = get_pair_images(voxdims=["2","2"]) 
  image1 = nibabel.load(images[0])
  image2 = nibabel.load(images[1]) 
  pdmask = make_binary_deletion_mask([image1,image2]) 
  assert_equal(numpy.unique(pdmask)[0],0.0)
  assert_equal(numpy.unique(pdmask)[1],1.0)
  assert_false(numpy.isnan(pdmask).any())
  assert_false(numpy.isinf(pdmask).any())   
     
'''Test that binary deletion mask returns expected overlap given two images, nans and zeros'''
def test_binary_deletion_vector():

  mr_directory = get_data_directory()
  
  # We will generate data with the following overlap percentages
  overlap_percents = [0.0,0.25,0.5,0.75,1.0]
  for overlap in overlap_percents:
    vector_length = 10000
    image_vector1 = numpy.zeros((vector_length))
    image_vector2 = numpy.zeros((vector_length))
    number_overlap_voxels = int(numpy.floor(overlap*vector_length))
    remaining_voxels = int(vector_length - number_overlap_voxels)
    idx = range(0,vector_length)
    # We break the remaining voxels into 4 groups:
    # - nans that will overlap
    # - zeros that will overlap (no change to images here, already zeros)
    # - nans in image1, random sample of values in image2
    # - zeros in image2, random sample of values in image1 
    group_size = remaining_voxels/4
    if overlap != 0.0:
      # Here are the overlapping voxels for each image
      overlap_idx = range(0,number_overlap_voxels)
      image_vector1[overlap_idx] = 1
      image_vector2[overlap_idx] = 1 
    if overlap != 1.0: 
      # Nans that will overlap
      nans_overlap_idx = range(number_overlap_voxels,(number_overlap_voxels+group_size))
      image_vector1[nans_overlap_idx] = numpy.nan
      image_vector2[nans_overlap_idx] = numpy.nan
      # Nans in image1, random sample of values in image 2
      start = number_overlap_voxels+group_size
      end = number_overlap_voxels+2*group_size
      nans_image1 = idx[start:end]
      values_image2 = range(nans_image1[-1],(nans_image1[-1] + int(group_size/2)))
      image_vector1[nans_image1] = numpy.nan
      image_vector2[values_image2] = 0.5
      # Zeros in image2, random sample of values in image 1
      start = number_overlap_voxels+2*group_size
      end = number_overlap_voxels+3*group_size
      zeros_image2 = idx[start:end]
      values_image1 = range(zeros_image2[-1],(zeros_image2[-1] + int(group_size/2)))
      image_vector1[values_image1] = 0.75
    # Create nifti images and pdmask
    pdmask = make_binary_deletion_vector([image_vector1,image_vector2]) 
    actual_overlap = len(numpy.where(pdmask!=0)[0])
    print "Overlap %s percent: should have %s, actual %s" %(overlap,number_overlap_voxels,actual_overlap)
    assert_equal(actual_overlap,number_overlap_voxels)
   
    # Also check that is binary
    if overlap != 0 and overlap != 1:
      assert_equal(numpy.unique(pdmask)[0],0)
      assert_equal(numpy.unique(pdmask)[1],1)

    if overlap == 0:
      assert_equal(numpy.unique(pdmask)[0],0)

    if overlap == 1:
      assert_equal(numpy.unique(pdmask)[0],1)

