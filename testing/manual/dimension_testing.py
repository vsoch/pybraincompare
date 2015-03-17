# This script will test how much precision we lose with different voxel dimensions.

import nibabel
import pandas
from glob import glob
import random
import os
from nilearn.image import resample_img
from testing_functions import run_scatterplot_compare_voxdim, get_atlas
from compare.mrutils import resample_images_ref, get_standard_mask
from compare import atlas as Atlas

# The ability to specify a voxel dimension has been removed, so this test code is for documentation only
voxdims = [[3,3,3],[4,4,4],[5,5,5],[6,6,6],[7,7,7],[8,8,8],[9,9,9]]

# We will be testing 10 images
images = glob("/home/vanessa/Documents/Work/BRAINMETA/IMAGE_COMPARISON/mr/resampled/*.nii.gz")
images = random.sample(images,100)
image_names = [os.path.split(x)[1] for x in images]
atlas = get_atlas()
standard = get_standard_mask(software="FSL")

# We will use a threshold of 0
thresh = 0.0

gs = pandas.DataFrame(columns=image_names)
for i in range(0,len(images)):
  image1 = images[i]
  image_name = image_names[i]
  print "Processing %s of %s" %(i+1,len(images))
  single_gs = []
  for image2 in images:
    mrs = [image1,image2]
    df_single,nv_corr,pbc_corr =  run_scatterplot_compare_voxdim(images=mrs,image_names=["image 1","image 2"],threshold=thresh,reference_mask=standard,browser_view=False,resample_dim=[2,2,2])
    single_gs.append(pbc_corr["No Label"])
  gs.loc[image_name] = single_gs

gs.to_csv("gs_voxel_comparison_10.tsv",sep="\t")

# Now we will resample, and calculate correlations at differnt voxel dimensions
image_names.append("voxdim")
resampled = pandas.DataFrame(columns=image_names)
for voxdim in voxdims:
  print "Processing voxdim 10 %s" %(voxdim)  
  for i in range(0,len(images)):
    image1 = images[i]
    image_name = image_names[i]
    print "Processing %s of %s" %(i+1,len(images))
    single_rs = []
    for image2 in images:
      mrs = [image1,image2]
      df_single,nv_corr,pbc_corr = run_scatterplot_compare_voxdim(images=mrs,image_names=["image 1","image 2"],threshold=thresh,reference_mask=standard,browser_view=False,resample_dim=voxdim)
      single_rs.append(pbc_corr["No Label"])
    single_rs.append(voxdim)
    resampled.loc["%s_%s" %(image_name,voxdim[0])] = single_rs

resampled.to_csv("resampled_voxel_comparison_10.tsv",sep="\t")
