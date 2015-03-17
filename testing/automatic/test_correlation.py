#!/usr/bin/python

"""
Test that regional and whole brain correlation scores remain consistent
"""
from testing_functions import run_scatterplot_compare_correlation, generate_thresholds, calculate_pybraincompare_pearson
from compare.mrutils import resample_images_ref, make_binary_deletion_mask, do_mask
from numpy.testing import assert_array_equal, assert_almost_equal, assert_equal
from neurovault_functions import calculate_voxelwise_pearson_similarity
from compare.maths import do_pairwise_correlation
from nose.tools import assert_true, assert_false
from compare import compare, atlas as Atlas
from nilearn.image import resample_img
from template.visual import view
from scipy.stats import norm
import testing_functions
import nibabel
import random
import pandas
import numpy
import os

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

    # We should have the same number
    assert_equal(len(nv_corrs),len(pbc_corrs))

    # And they should almost have equal precision
    for c in range(0,len(pbc_corrs)):
      assert_almost_equal(nv_corrs[c],pbc_corrs[c],decimal=4)

    
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
      pbc_scores.append(pbc_corr)
      df = df.append(df_single)

    # We should have the same number
    assert_equal(len(scores),len(pbc_scores))

    # And they should be equal
    for c in range(0,len(pbc_scores)):
      assert_almost_equal(scores[c],pbc_scores[c],decimal=4)

    # Regional correlation scores should also be equal
    data_directory = os.path.join(os.path.abspath(os.path.dirname(testing_functions.__file__)),"data") 
    df_standard = pandas.read_csv("%s/regional_scores.tsv" %(data_directory),sep="\t")
    for row in df_standard.iterrows():
      subset = df[df.ATLAS_LABELS==row[1].ATLAS_LABELS]
      subset = subset[subset.threshold==row[1].threshold]
      assert_almost_equal(subset.ATLAS_CORR.values[0],row[1].ATLAS_CORR,decimal=4)
    

# https://github.com/NeuroVault/NeuroVault/issues/133#issuecomment-74464393
'''Test that pybraincompare returns same simulated correlations'''
def test_simulated_correlations():

  # Get standard brain mask
  thresholds,images,standard = setup_func()

  # Generate random data inside brain mask, run 10 iterations
  standard = nibabel.load(standard)
  number_values = len(numpy.where(standard.get_data()!=0)[0])
  numpy.random.seed(9191986)
  data1 = norm.rvs(size=number_values)
  for x in range(0,10):  
    data2 = norm.rvs(size=number_values)
    means = [data1.mean(), data2.mean()]      # should be essentially 0 
    stds = [data1.std(), data2.std()] # should be essentially 1
    corr = random.uniform(0,1)        # some correlation
    covs = [[stds[0]**2         , stds[0]*stds[1]*corr], 
           [stds[0]*stds[1]*corr,           stds[1]**2]] 
    m = numpy.random.multivariate_normal(means, covs, number_values).T
      
    # Put into faux nifti images
    mr1 = numpy.zeros(standard.shape)
    mr1[standard.get_data()!=0] = m[0]
    mr1 = nibabel.nifti1.Nifti1Image(mr1,affine=standard.get_affine(),header=standard.get_header())
    mr2 = numpy.zeros(standard.shape)
    mr2[standard.get_data()!=0] = m[1]
    mr2 = nibabel.nifti1.Nifti1Image(mr2,affine=standard.get_affine(),header=standard.get_header())  
    score = calculate_pybraincompare_pearson([mr1,mr2])  
    assert_almost_equal(corr,score,decimal=2)
