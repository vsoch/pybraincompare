#!/usr/bin/env python2

import pandas
from glob import glob
import nibabel as nib
from pybraincompare.report.qa import is_thresholded, is_only_positive, get_voxel_range, central_tendency

# Here is a set of 144 images, these are 9 openfmri studies in Neurovault, resampled to MNI 2mm
mrs = glob("/home/vanessa/Documents/Work/BRAINMETA/IMAGE_COMPARISON/mr/resampled/*.nii.gz")
nifti_objs = [nib.load(mr) for mr in mrs]

# We want to include within this brain mask
brain_mask = nib.load("/usr/share/fsl/data/standard/MNI152_T1_2mm_brain_mask.nii.gz")

# Are the images masked at some threshold?
threshold_tests = [is_thresholded(mr,brain_mask,threshold=0.95) for mr in nifti_objs] 

# Are the images only positive values?
positive_tests = [is_only_positive(mr) for mr in nifti_objs]

# Get the minimum and maximum values for each map
range_results = [get_voxel_range(mr) for mr in nifti_objs]

# Get the mean, std, variance, etc for each image
stats = [central_tendency(mr) for mr in nifti_objs] 

result = pandas.DataFrame(columns=["image","threshold_flag","percent_nonzero","only_pos","mean","median","sd","variance","min","max"])

count = 0
for t in range(0,len(threshold_tests)):
  thresh = threshold_tests[t]
  ranges = range_results[t]
  stat = stats[t]
  result.loc[count] = [mrs[t],thresh[0],thresh[1],positive_tests[t],stat["mean"],stat["med"],stat["std"],stat["var"],ranges[0],ranges[1]]
  count = count+1

result.to_csv("/home/vanessa/Desktop/threshold_report.tsv",sep="\t")
