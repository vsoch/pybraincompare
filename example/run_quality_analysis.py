#!/usr/bin/env python2

from glob import glob
from compare.qa import run_qa

# Here is a set of 144 images, these are 9 openfmri studies in Neurovault, resampled to MNI 2mm
mrs = glob("/home/vanessa/Documents/Work/BRAINMETA/IMAGE_COMPARISON/mr/resampled/*.nii.gz")

# Run quality analysis
outdir = "/home/vanessa/Desktop/test"
run_qa(mrs,software="FREESURFER",html_dir=outdir,voxdim=[2,2,2],outlier_sds=6,investigator="Vanessa")

