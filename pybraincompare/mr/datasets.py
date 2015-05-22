'''
datasets.py: part of pybraincompare package
Return sets of images or atlas files

'''

import os
import nibabel as nib
import numpy
import pybraincompare.compare.atlas as Atlas
from nilearn.image import resample_img

# Get data directory
def get_data_directory():
    mr_directory = os.path.join(os.path.abspath(os.path.dirname(Atlas.__file__) + "/.."),"mr") 
    return mr_directory

# Return paths to pybraincompare atlas
'''Returns path to MNI atlas in MNI 152 space'''
def get_mni_atlas(voxdims=["2","8"],views=None):
    atlas_directory = get_data_directory()
    atlas_xml = "%s/MNI.xml" %(atlas_directory)
    atlases = dict()
    for dim in voxdims:
        atlas_file = "%s/MNI-maxprob-thr25-%smm.nii" %(atlas_directory,dim)
        if views == None: # return all orthogonal
            atlas = Atlas.atlas(atlas_xml,atlas_file)
        else:
            atlas = Atlas.atlas(atlas_xml,atlas_file,views=views)
        atlases[dim] = atlas
    return atlases

# Get pair of images, only available are currently 2 and 8 mm.
def get_pair_images(voxdims=["2","2"]):
    mr_directory = get_data_directory()
    image1 = "%s/%smm16_zstat1_1.nii" %(mr_directory,voxdims[0])
    image2 = "%s/%smm16_zstat3_1.nii" %(mr_directory,voxdims[1])
    return [image1,image2]

# Get pybraincompare standard brain (from FSL) if user doesn't have software
def get_standard_brain(voxdim=2):
    mr_directory = get_data_directory()
    brain = "%s/MNI152_T1_%smm_brain.nii.gz" %(mr_directory,voxdim)
    if not os.path.exists(brain):
        brain = nib.load("%s/MNI152_T1_2mm_brain.nii.gz" %(mr_directory))
        brain = resample_img(brain,target_affine=numpy.diag([voxdim,voxdim,voxdim]))
        return brain
    else:
        return nib.load(brain)

# Get pybraincompare standard brain mask (from FSL) if user doesn't have software
def get_standard_mask(voxdim=2):
    mr_directory = get_data_directory()
    mask = "%s/MNI152_T1_%smm_brain_mask.nii.gz" %(mr_directory,voxdim)
    if not os.path.exists(mask):
        mask = nib.load("%s/MNI152_T1_2mm_brain_mask.nii.gz" %(mr_directory))
        mask = resample_img(mask,target_affine=numpy.diag([voxdim,voxdim,voxdim]),interpolation="nearest")
        return mask
    else:
        return nib.load(mask)
