#!/usr/bin/python

# This script will test the scatterplot compare for different thresholds of images
# We want to be sure that when the number of voxels for comparison is < 3, the interface shows message

from testing_functions import run_scatterplot_compare_threshold
from compare import atlas as Atlas

thresholds = [0.0,0.5,1.0,1.5,1.96,2.0,2.58,3.02]

# We will use our speedy 8mm mask, and images.
# We don't need to specify atlas - now part of package
image1 = "../mr/8mm16_zstat1_1.nii"
image2 = "../mr/8mm16_zstat3_1.nii"
standard = "../mr/MNI152_T1_8mm_brain_mask.nii.gz"
images = [image1,image2]

# Here we will run scatterplot compare for each threshold
for thresh in thresholds:
  run_scatterplot_compare_threshold(images=images,image_names=["image 1","image 2"],threshold=thresh,reference_mask=standard,browser_view=True)

# 13838 overlapping voxels at threshold 0.0
# 647 overlapping voxels at threshold 0.5
# 153 overlapping voxels at threshold 1.0
# 22 overlapping voxels at threshold 1.5
# 8 overlapping voxels at threshold 1.96
# 8 overlapping voxels at threshold 2.0
# 1 overlapping voxels at threshold 2.58
# 0 overlapping voxels at threshold 3.02
# 0 overlapping voxels at threshold 3.5
# 0 overlapping voxels at threshold 4.0
# 0 overlapping voxels at threshold 4.5
# 0 overlapping voxels at threshold 5.0
# 0 overlapping voxels at threshold 5.5
# 0 overlapping voxels at threshold 6.0


