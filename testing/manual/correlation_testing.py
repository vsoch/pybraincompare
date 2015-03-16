#!/usr/bin/python

# This script will test the scatterplot compare pearson values against neurovault

from testing_functions import run_scatterplot_compare_correlation, generate_thresholds
import pandas

thresholds = [0.0,0.5,1.0,1.5,1.96,2.0,2.58,3.02]
thresholds = generate_thresholds()

# Use 8mm resampled images for speed
image1 = "../../mr/8mm16_zstat1_1.nii"
image2 = "../../mr/8mm16_zstat3_1.nii"
standard = "../../mr/MNI152_T1_8mm_brain_mask.nii.gz"
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
# [{'No Label': 0.24239542},
# {'No Label': 0.37818813},
# {'No Label': 0.58678013},
# {'No Label': 0.84492999},
# {'No Label': 0.52579623},
# {'No Label': 0.52579623},
# {'No Label': nan},
# {'No Label': nan}]

df.to_csv("pbc_regional_corrs.tsv",sep="\t",index=False)
