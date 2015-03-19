#!/usr/bin/python

import os
import numpy
import pylab as plt
import nibabel as nib
from scipy.stats.stats import pearsonr
from pybraincompare.testing.testing_functions import make_binary_deletion_mask
from nilearn.image import resample_img

# Edited for pybraincompare testing - 
#   - no longer taking a resample dim, images going in will be same 
def calculate_voxelwise_pearson_similarity(image1, image2):

    images_resamp = [image1,image2]    
    for image_nii, image_obj in zip(images_resamp, [image1, image2]):
        if len(numpy.squeeze(image_nii.get_data()).shape) != 3:
            raise Exception("Image %s (id=%d) has incorrect number of dimensions %s"%(image_obj.name, image_obj.id, str(image_nii.get_data().shape)))

    # Calculate correlation only on voxels that are in both maps (not zero, and not nan)
    binary_mask = make_binary_deletion_mask(images_resamp)
    image1_res = images_resamp[0]
    image2_res = images_resamp[1]
    

    # Calculate correlation with voxels within mask
    return pearsonr(numpy.squeeze(image1_res.get_data())[binary_mask == 1],
                    numpy.squeeze(image2_res.get_data())[binary_mask == 1])[0]



'''Resample single image to match some other reference (continuous interpolation, not for atlas)'''


def resample_single_img_ref(image, reference):
    return resample_img(image, target_affine=reference.get_affine(), target_shape=reference.get_shape())


'''Resample multiple image to match some other reference (continuous interpolation, not for atlas)'''


def resample_multi_images_ref(images, mask, resample_dim):
    affine = numpy.diag(resample_dim)
    # Prepare the reference
    reference = nib.load(mask)
    reference_resamp = resample_img(reference, target_affine=affine)
    # Resample images to match reference
    if isinstance(images, str):
        images = [images]
    images_resamp = []
    for image in images:
        im = nib.load(image)
        images_resamp.append(resample_single_img_ref(im, reference_resamp))
    return images_resamp, reference_resamp
