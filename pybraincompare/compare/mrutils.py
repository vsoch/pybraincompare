'''
mrutils.py: part of pybraincompare package
Functions work with brain maps

'''

from pybraincompare.template.futils import get_name
from pybraincompare.report.image import make_anat_image
from nilearn.masking import apply_mask, compute_epi_mask
from nilearn.image import resample_img
import subprocess
import os
import numpy
import nibabel


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

'''Returns nibabel nifti objects from a list of filenames and/or nibabel objects'''
def get_nii_obj(images):
    images_nii = []
    if isinstance(images,str): 
        images = [images]
    if isinstance(images,nibabel.nifti1.Nifti1Image):
        return [images]
    for i in range(0,len(images)):
        image = images[i]    
        if not isinstance(image,nibabel.nifti1.Nifti1Image): 
            image = nibabel.load(image)
        images_nii.append(image)
    return images_nii


# RESAMPLING -----------------------------------------------------------------------------

'''Resample many images to single reference
images: should be list of image files or nibabel images
reference: single image file or nibabel image
'''
def resample_images_ref(images,reference,interpolation,resample_dim=None):

  if isinstance(reference,str): reference = nibabel.load(reference)
  if resample_dim:
    affine = numpy.diag(resample_dim)
    reference = resample_img(reference, target_affine=affine)

  # Resample images to match reference mask affine and shape
  if not isinstance(images,list): images = [images]
  images_nii = get_nii_obj(images)

  # Make sure we don't have any with singleton dimension
  images = squeeze_fourth_dimension(images_nii)

  images_resamp = []
  for image in images_nii:
    # Only resample if the image is different from the reference
    if not (image.get_affine() == reference.get_affine()).all():
      resampled_img = resample_img(image,target_affine=reference.get_affine(), 
                                 target_shape=reference.shape,
                                 interpolation=interpolation)
    else: resampled_img = image
    images_resamp.append(resampled_img)
  return images_resamp, reference

'''squeeze out extra fourth dimension'''
def squeeze_fourth_dimension(images):
  shapes = [len(i.shape) == 4 for i in images]
  if any(v is True for v in shapes):
    squeezed=[]
    for image in images:
      squeezed_image = nibabel.Nifti1Image(numpy.squeeze(image.get_data()),affine=image.get_affine(),header=image.get_header())
      squeezed.append(squeezed_image)
    return squeezed
  else:
    return images

# MASKING --------------------------------------------------------------------------------
'''Mask registered images - should already be in same space
images: a list of nifti1 objects [same size and shape]
mask: a nifti1 object mask [same size and shape]
'''
def do_mask(images,mask):

  # If we only have one image
  if isinstance(images,nibabel.nifti1.Nifti1Image): images = [images]

  # Make sure images are 3d (squeeze out extra dimension)
  images = squeeze_fourth_dimension(images)

  # Don't trust that mask is binary  
  mask_bin = mask.get_data().astype(bool).astype(int)
  mask = nibabel.nifti1.Nifti1Image(mask_bin,affine=mask.get_affine(),header=mask.get_header())

  # if ensure_finite is True, nans and infs get replaced by zeros
  try:
    masked_data = apply_mask(images, mask, dtype='f', smoothing_fwhm=None, ensure_finite=False)
    return masked_data
  except ValueError:
    print "Reference and images affines do not match, or given mask and images, all data is masked." 
    return numpy.nan
  
'''Make binary deletion mask (pairwise deletion) - intersection of nonzero and non-nan values'''
def make_binary_deletion_mask(images):
    if isinstance(images, nibabel.nifti1.Nifti1Image):
        images = [images]
    images_data = [numpy.squeeze(image.get_data()) for image in images]
    mask = numpy.ones(images_data[0].shape)
    for image_data in images_data:
        mask *= (image_data != 0) & ~numpy.isnan(image_data)
    return mask

'''Make binary deletion vector (pairwise deletion) - intersection of nonzero and non-nan values'''
def make_binary_deletion_vector(image_vectors):
    mask = numpy.ones(image_vectors[0].shape)
    mask *= (image_vectors[0] != 0) & ~numpy.isnan(image_vectors[0])
    mask *= (image_vectors[1] != 0) & ~numpy.isnan(image_vectors[1])
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

# THRESHOLDING --------------------------------------------------------------------------------

# Generate thresholds
def generate_thresholds(lower=0,upper=4,by=0.01):
  thresholds = []
  for ii in range(lower,upper):
    thresholds = thresholds + [(float(x) * by)+ii for x in range(0,100)]
  return thresholds

''' Threshold an image 
image1: nibabel nifti1 image
thresh: a threshold value for the image
direction:  posneg: include both positive and negative values [default]
            pos: include only positive values
            neg: include only negative values
'''
def apply_threshold(image1,thresh,direction="posneg"):
  data = image1.get_data()
  tmp = numpy.zeros(image1.shape)  
  if direction == "posneg":
    tmp[numpy.abs(data) >= thresh] = data[numpy.abs(data) >= thresh]  
  elif direction == "pos":
    tmp[data >= thresh] = data[data >= thresh]  
  elif direction == "neg":
    tmp[data <= thresh] = data[data <= thresh]  
  new_image = nibabel.Nifti1Image(tmp,affine = image1.get_affine(),header=image1.get_header())
  return new_image
