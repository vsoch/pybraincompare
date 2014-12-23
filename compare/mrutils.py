import nibabel
import os
import numpy
from nilearn.image import resample_img
from nilearn.masking import apply_mask

# GET MR IMAGE FUNCTIONS------------------------------------------------------------------
'''Returns reference image from FSL or FREESURFER'''
def get_standard_mask(software):
  if software == "FSL":
    reference = os.path.join(os.environ['FSL_DIR'],'data', 'standard', 'MNI152_T1_2mm_brain_mask.nii.gz')
  elif software == "FREESURFER":
    reference = os.path.join(os.environ['FREESURFER_HOME'],'subjects', 'fsaverage', 'mri', 'brainmask.nii.gz')
  return reference
  #TODO: How do I trigger an error?  


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

# MASKING --------------------------------------------------------------------------------
def do_mask(images,mask,resample_dim):
  
  affine = numpy.diag(resample_dim)

  # Prepare the reference
  reference = _load_image(mask)
  reference_resamp = _resample_img(reference,affine)  

  images_resamp = []
  for image in images:
    im = _load_image(image)
    image_resamp = _resample_img(im,affine)
    images_resamp.append(image_resamp)

  return apply_mask(images_resamp, reference_resamp, dtype='f', smoothing_fwhm=None, ensure_finite=True)
