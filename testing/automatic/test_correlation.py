#!/usr/bin/python

"""
Test that regional and whole brain correlation scores remain consistent
"""

from compare.mrutils import resample_images_ref, make_binary_deletion_mask, do_mask
from compare.maths import do_pairwise_correlation
from compare import compare, atlas as Atlas
from nilearn.image import resample_img
from testing_functions import run_scatterplot_compare_correlation, generate_thresholds
from neurovault_functions import calculate_voxelwise_pearson_similarity
from template.visual import view
import testing_functions
import pandas
import numpy
import nibabel
import os

from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from nose.tools import assert_true, assert_false

def setup_func():
    thresholds = [0.0,0.5,1.0,1.5,1.96,2.0]
    mr_directory = os.path.join(os.path.abspath(os.path.dirname(testing_functions.__file__) + "/../.."),"mr") 

    # Use 8mm resampled images for speed
    image1 = "%s/8mm16_zstat1_1.nii" %(mr_directory)
    image2 = "%s/8mm16_zstat3_1.nii" %(mr_directory)
    standard = "%s/MNI152_T1_8mm_brain_mask.nii.gz" %(mr_directory)
    images = [image1,image2]
    return thresholds,images,standard

'''Test pybraincompare correlation method against neurovault method'''
def test_pbc_vs_neurovault():

    thresholds,images,standard = setup_func()
    
    # Here we will output scatterplot compare correlations for each threshold
    df = pandas.DataFrame()
    nv_corrs = []  # Whole brain correlation calculated with neurovault
    pbc_corrs = [] # Whole brain correlation calculated with pyraincompare
    for thresh in thresholds:
      df_single,nv_corr,pbc_corr = run_scatterplot_compare_correlation(images=images,
                                                                       image_names=["image 1","image 2"],
                                                                       threshold=thresh,
                                                                       reference_mask=standard,
                                                                       browser_view=False)
      nv_corrs.append(nv_corr)
      pbc_corrs.append(pbc_corr)
      df = df.append(df_single)

    pbc_scores = []
    for p in pbc_corrs:
        pbc_scores.append(p["No Label"])
    print pbc_scores
    # We should have the same number
    assert_equal(len(nv_corrs),len(pbc_scores))

    # And they should almost have equal precision
    for c in range(0,len(pbc_corrs)):
      assert_almost_equal(nv_corrs[c],pbc_scores[c],decimal=4)

    
'''Test that pybraincompare scores are not changing'''
def test_pbc_correlation_consistent():

    thresholds,images,standard = setup_func()
    # These are the scores we should get for the thresholds
    scores = [0.24239542,0.37818813,0.58678013,0.84492999,0.52579623,0.52579623]
   
    # Here we will output scatterplot compare correlations for each threshold
    df = pandas.DataFrame()
    pbc_corrs = [] # Whole brain correlation calculated with pyraincompare
    for thresh in thresholds:
      df_single,nv_corr,pbc_corr = run_scatterplot_compare_correlation(images=images,
                                                                       image_names=["image 1","image 2"],
                                                                       threshold=thresh,
                                                                       reference_mask=standard,
                                                                       browser_view=False)
      pbc_corrs.append(pbc_corr)
      df = df.append(df_single)

    
    pbc_scores = []
    for p in pbc_corrs:
        pbc_scores.append(p["No Label"])

    # We should have the same number
    assert_equal(len(scores),len(pbc_scores))

    # And they should be equal
    for c in range(0,len(pbc_corrs)):
      assert_almost_equal(scores[c],pbc_scores[c],decimal=4)

    # Regional correlation scores should also be equal
    data_directory = os.path.join(os.path.abspath(os.path.dirname(testing_functions.__file__)),"data") 
    df_standard = pandas.read_csv("%s/regional_scores.tsv" %(data_directory),sep="\t")
    for row in df_standard.iterrows():
      subset = df[df.ATLAS_LABELS==row[1].ATLAS_LABELS]
      subset = subset[subset.threshold==row[1].threshold]
      assert_almost_equal(subset.ATLAS_CORR.values[0],row[1].ATLAS_CORR,decimal=4)
    
