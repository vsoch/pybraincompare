'''
transformation.py: part of pybraincompare package
Return transformations of images

'''
from pybraincompare.mr.datasets import get_standard_brain
from pybraincompare.compare.mrutils import get_nii_obj
from nilearn.image import resample_img
import nibabel as nib
import numpy
import os

# Return resampled transformation image as vector
def make_resampled_transformation_vector(nii_obj,resample_dim=[4,4,4],standard_mask=True):

    resamp_nii = make_resampled_transformation(nii_obj,resample_dim,standard_mask)
    if standard_mask:
        standard = get_standard_brain(voxdim=resample_dim[0])
        return resamp_nii.get_data()[standard.get_data()!=0]
    else:
        return resamp_nii.get_data().flatten()


# Make a resampled image transformation
def make_resampled_transformation(nii_obj,resample_dim=[4,4,4],standard_mask=True):

    nii_obj = get_nii_obj(nii_obj)[0]

    # To set 0s to nan, we need to have float64 data type
    true_zeros = numpy.zeros(nii_obj.shape) # default data_type is float64
    true_zeros[:] = nii_obj.get_data()
    true_zeros[true_zeros==0] = numpy.nan

    # Resample image to 4mm voxel, nans are preserved
    true_zeros = nib.nifti1.Nifti1Image(true_zeros,affine=nii_obj.get_affine())
    
    # Standard brain masking
    if standard_mask == True:
        standard = get_standard_brain(voxdim=resample_dim[0])
        true_zeros = resample_img(true_zeros,target_affine=standard.get_affine(), 
                                  target_shape=standard.shape)
      
        # Mask the image 
        masked_true_zeros = numpy.zeros(true_zeros.shape)
        masked_true_zeros[standard.get_data()!=0] = true_zeros.get_data()[standard.get_data()!=0]
        true_zeros = nib.nifti1.Nifti1Image(masked_true_zeros,affine=true_zeros.get_affine())

    # or just resample
    else: 
        if (resample_dim != numpy.diag(true_zeros.get_affine())[0:3]).all():
            true_zeros = resample_img(true_zeros,target_affine=numpy.diag(resample_dim))

    return true_zeros
