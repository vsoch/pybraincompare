#!/usr/bin/python

"""
Test transformation functions
"""
from pybraincompare.mr.transformation import make_resampled_transformation_vector, make_resampled_transformation
from pybraincompare.mr.datasets import get_pair_images, get_standard_brain
from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from nose.tools import assert_true, assert_false
import nibabel
import random
import pandas
import numpy
import os

def test_masked_transformation():
    image1 = nibabel.load(get_pair_images()[0])
    brain_4mm = get_standard_brain(4)
    nonzero_voxels = brain_4mm.get_data()[brain_4mm.get_data()!=0].shape[0]
    image1_vector = make_resampled_transformation_vector(image1,resample_dim=[4,4,4],standard_mask=True)
    assert_equal(nonzero_voxels,len(image1_vector))

    brain_8mm = get_standard_brain(8)
    nonzero_voxels = brain_8mm.get_data()[brain_8mm.get_data()!=0].shape[0]
    image1_vector = make_resampled_transformation_vector(image1,resample_dim=[8,8,8],standard_mask=True)
    assert_equal(nonzero_voxels,len(image1_vector))

def test_unmasked_transformation():
    image1 = nibabel.load(get_pair_images()[0])
    nonzero_voxels = len(image1.get_data().flatten())
    image1_vector = make_resampled_transformation_vector(image1,resample_dim=[2,2,2],standard_mask=False)
    assert_equal(nonzero_voxels,len(image1_vector))

    brain_4mm = get_standard_brain(4)
    nonzero_voxels = len(brain_4mm.get_data().flatten())
    image1_vector = make_resampled_transformation_vector(image1,resample_dim=[4,4,4],standard_mask=False)
    assert_equal(nonzero_voxels,len(image1_vector))
