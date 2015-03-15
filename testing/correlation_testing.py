#!/usr/bin/python

# This script will test the scatterplot compare pearson values against neurovault

from testing_functions import run_scatterplot_compare_correlation
import pandas

thresholds = [0.0,0.5,1.0,1.5,1.96,2.0,2.58,3.02]

# Use 8mm resampled images for speed
image1 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/8mm16_zstat1_1.nii"
image2 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/8mm16_zstat3_1.nii"
standard = "/usr/share/fsl/5.0/data/standard/MNI152_T1_8mm_brain_mask.nii.gz"
images = [image1,image2]

# Here we will output scatterplot compare correlations for each threshold
df = pandas.DataFrame()
nv_corrs = []  # Whole brain correlation calculated with NeuroVault code
pbc_corrs = [] # Whole brain correlation calculated with pyraincompare
for thresh in thresholds:
  df_single,nv_corr,pbc_corr = run_scatterplot_compare_correlation(images=images,image_names=["image 1","image 2"],threshold=thresh,reference_mask=standard,browser_view=False)
  nv_corrs.append(nv_corr)
  pbc_corrs.append(pbc_corr)
  df = df.append(df_single)

# Confirmation that neurovault and pybraincompare methods are equivalent - we return same thing
# nv_corrs
# 0.24239566035135185
# 0.37818797382861302
# 0.58678004796794958
# 0.8449301668580359
# 0.52579617697298064
# 0.52579617697298064
# nan
# nan

# pbc_corrs
# 0.24239542, 3.3100558253633504e-184)},
# 0.37818813, 1.98323308155013e-23)},
# 0.58678013, 1.5801695831852542e-15)},
# 0.84492999, 7.5274193127007272e-07)},
# 0.52579623, 0.18076500482241567)},
# 0.52579623, 0.18076500482241567)},
# nan
# nan

df.to_csv("/home/vanessa/Desktop/pbc_regional_corrs.tsv",sep="\t",index=False)
