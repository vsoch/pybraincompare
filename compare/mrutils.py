'''
mrutils.py: part of pybraincompare package
Functions work with brain maps

'''

import nibabel
import subprocess
import os
import numpy
from nilearn.image import resample_img
from report.plots import make_anat_image
from nilearn.masking import apply_mask, compute_epi_mask

# GET MR IMAGE FUNCTIONS------------------------------------------------------------------
'''Returns reference mask from FSL or FREESURFER'''
def get_standard_mask(software):
  if software == "FSL":
    reference = os.path.join(os.environ['FSL_DIR'],'data', 'standard', 'MNI152_T1_2mm_brain_mask.nii.gz')
  elif software == "FREESURFER":
    reference = os.path.join(os.environ['FREESURFER_HOME'],'subjects', 'fsaverage', 'mri', 'brainmask.mgz')
  return reference

'''Returns reference brain from FSL or FREESURFER'''
def get_standard_brain(software):
  if software == "FSL":
    reference = os.path.join(os.environ['FSL_DIR'],'data', 'standard', 'MNI152_T1_2mm_brain.nii.gz')
  elif software == "FREESURFER":
    reference = os.path.join(os.environ['FREESURFER_HOME'],'subjects', 'fsaverage', 'mri', 'brain.mgz')
  return reference

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
def _resample_img(image,affine,interpolation="continuous"):
  return resample_img(image, target_affine=affine)


'''Resample image to match some other reference'''
def _resample_img_ref(image,reference,interpolation):
  return resample_img(image, target_affine=reference.get_affine(), target_shape=reference.get_shape(),interpolation=interpolation)

'''Resample many images to single reference'''
def _resample_images_ref(images,mask,resample_dim,interpolation):
  affine = numpy.diag(resample_dim)

  # Prepare the reference
  reference = _load_image(mask)
  reference_resamp = _resample_img(reference,affine)  

  # Resample images to match reference
  if isinstance(images,str): images = [images]
  images_resamp = []
  for image in images:
    im = _load_image(image)
    images_resamp.append(_resample_img_ref(im,reference_resamp,interpolation))

  return images_resamp, reference_resamp

'''squeeze out extra fourth dimension'''
def squeeze_fourth_dimension(images):
  squeezed=[]
  for image in images:
    squeezed_image = nibabel.Nifti1Image(numpy.squeeze(image.get_data()),affine=image.get_affine(),header=image.get_header())
    squeezed.append(squeezed_image)
  return squeezed

# MASKING --------------------------------------------------------------------------------
'''Mask and resample registered images'''
def do_mask(images,mask,resample_dim,interpolation="continuous",second_mask=None):

  # Resample images to reference and new voxel size
  images_resamp, reference_resamp = _resample_images_ref(images,mask,resample_dim,interpolation)  
  # Make sure images are 3d (squeeze out extra dimension)
  images_resamp = squeeze_fourth_dimension(images_resamp)
  # Assume needs to be binarized to be mask [FREESURFER IM LOOKING AT YOU]
  reference = compute_epi_mask(reference_resamp)

  if second_mask != None:
    second_mask_resamp = resample_img(second_mask, target_affine=reference_resamp.get_affine(), target_shape=reference_resamp.get_shape(),interpolation="nearest")
    ref_tmp = numpy.logical_and(reference.get_data(), second_mask_resamp.get_data()).astype(int)
    reference = nibabel.Nifti1Image(ref_tmp,header=reference_resamp.get_header(),affine=reference_resamp.get_affine())

  if isinstance(images_resamp,str): images_resamp = [images_resamp]
  return apply_mask(images_resamp, reference, dtype='f', smoothing_fwhm=None, ensure_finite=True)

'''Make binary deletion mask (pairwise deletion) - intersection of nonzero and non-nan values'''
def make_binary_deletion_mask(images):
    if isinstance(images, nibabel.nifti1.Nifti1Image):
        images = [images]
    images_data = [numpy.squeeze(image.get_data()) for image in images]
    mask = numpy.ones(images_data[0].shape)
    for image_data in images_data:
        mask *= (image_data != 0) & ~numpy.isnan(image_data)
    return mask

'''make in out mask
Generate masked image, return two images: voxels in mask, and voxels outside
'''
def make_in_out_mask(mask_bin,mr_folder,masked_in,masked_out,img_dir,save_png=True):
  mr_in_mask = numpy.zeros(mask_bin.shape)
  mr_out_mask = numpy.zeros(mask_bin.shape)
  mr_out_mask[mask_bin.get_data()==0] = masked_out
  mr_out_mask = nibabel.Nifti1Image(mr_out_mask,affine=mask_bin.get_affine(),header=mask_bin.get_header())
  mr_in_mask[mask_bin.get_data()!=0] = masked_in
  mr_in_mask = nibabel.Nifti1Image(mr_in_mask,affine=mask_bin.get_affine(),header=mask_bin.get_header())
  nibabel.save(mr_in_mask,"%s/masked.nii" %(mr_folder))
  nibabel.save(mr_out_mask,"%s/masked_out.nii" %(mr_folder))
  if save_png:
    make_anat_image("%s/masked.nii" %(mr_folder),png_img_file="%s/masked.png" %(img_dir))
    make_anat_image("%s/masked_out.nii" %(mr_folder),png_img_file="%s/masked_out.png" %(img_dir))
  os.remove("%s/masked_out.nii" %(mr_folder))
  return mr_in_mask,mr_out_mask

