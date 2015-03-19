from pybraincompare.compare.mrutils import resample_images_ref, make_binary_deletion_mask, do_mask
from pybraincompare.compare.maths import calculate_pairwise_correlation
from pybraincompare.compare import compare, atlas as Atlas
from nilearn.image import resample_img
from pybraincompare.template.visual import view
import pandas
import numpy
import nibabel

# Generate thresholds
def generate_thresholds():
  thresholds = []
  for ii in range(0,4):
    thresholds = thresholds + [(float(x) * 0.01)+ii for x in range(0,100)]
  return thresholds

# Calculate a whole brain correlation with same procedure as in pybraincompare
def calculate_pybraincompare_pearson(images):
  pdmask = make_binary_deletion_mask(images)
  pdmask = nibabel.Nifti1Image(pdmask,header=images[0].get_header(),affine=images[0].get_affine())
  masked = do_mask(images=images,mask=pdmask)
  masked = pandas.DataFrame(numpy.transpose(masked))
  pbc_correlation = calculate_pairwise_correlation(masked[0],masked[1],corr_type="pearson")
  return pbc_correlation["No Label"]

# Threshold the image
def threshold_abs(image1,thresh):
  data = image1.get_data()
  tmp = numpy.zeros(image1.shape)  
  tmp[numpy.abs(data) >= thresh] = data[numpy.abs(data) >= thresh]  
  new_image = nibabel.Nifti1Image(tmp,affine = image1.get_affine(),header=image1.get_header())
  return new_image
