import nibabel
import subprocess
import os
import numpy
from nilearn.image import resample_img
from nilearn.masking import apply_mask, compute_epi_mask
from nilearn.masking import compute_epi_mask
from futils import make_tmp_folder
import tempfile
import shutil

# GET MR IMAGE FUNCTIONS------------------------------------------------------------------
'''Returns reference mask from FSL or FREESURFER'''
def get_standard_mask(software):
  if software == "FSL":
    reference = os.path.join(os.environ['FSL_DIR'],'data', 'standard', 'MNI152_T1_2mm_brain_mask.nii.gz')
  elif software == "FREESURFER":
    reference = os.path.join(os.environ['FREESURFER_HOME'],'subjects', 'fsaverage', 'mri', 'brainmask.nii.gz')
  return reference
  #TODO: How do I trigger an error?  

'''Returns reference brain from FSL or FREESURFER'''
def get_standard_brain(software):
  if software == "FSL":
    reference = os.path.join(os.environ['FSL_DIR'],'data', 'standard', 'MNI152_T1_2mm_brain.nii.gz')
  elif software == "FREESURFER":
    reference = os.path.join(os.environ['FREESURFER_HOME'],'subjects', 'fsaverage', 'mri', 'brain.nii.gz')
  return reference
  #TODO: Trigger an error

'''Return MNI transformations for registration'''
def get_standard_mat(software):
  if software == "FREESURFER":
    return os.path.join(os.environ['FREESURFER_HOME'],'average', 'mni152.register.dat')


# IMAGE FILE OPERATIONS ------------------------------------------------------------------
'''Load image using nibabel'''
def _load_image(image):
   return nibabel.load(image)

'''Load image data using nibabel'''
def _load_image_data(image):
   image = nibabel.load(image)
   return image.get_data()

# RESAMPLING -----------------------------------------------------------------------------
'''Resample image to specified voxel dimension'''
def _resample_img(image,affine):
  return resample_img(image, target_affine=affine)

'''Resample image to match some other reference'''
def _resample_img_ref(image,reference):
  return resample_img(image, target_affine=reference.get_affine(), target_shape=reference.get_shape())


# MASKING --------------------------------------------------------------------------------
'''Mask and resample registered images'''
def do_mask(images,mask,resample_dim):
  
  affine = numpy.diag(resample_dim)

  # Prepare the reference
  reference = _load_image(mask)
  reference_resamp = _resample_img(reference,affine)  

  # Resample images to match reference
  images_resamp = []
  for image in images:
    im = _load_image(image)
    images_resamp.append(_resample_img_ref(im,reference_resamp))

  # Assume needs to be binarized to be mask [FREESURFER IM LOOKING AT YOU]
  reference = compute_epi_mask(reference_resamp)

  return apply_mask(images_resamp, reference, dtype='f', smoothing_fwhm=None, ensure_finite=True)
