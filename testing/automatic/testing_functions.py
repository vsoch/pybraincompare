from compare.mrutils import resample_images_ref, make_binary_deletion_mask, do_mask
from neurovault_functions import calculate_voxelwise_pearson_similarity
from compare.maths import do_pairwise_correlation
from compare import compare, atlas as Atlas
from nilearn.image import resample_img
from template.visual import view
import pandas
import numpy
import nibabel

# Return paths to pybraincompare atlas
def get_atlas():
  atlas_file = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI-maxprob-thr25-8mm.nii"
  atlas_xml = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI.xml"
  atlas = Atlas.atlas(atlas_xml,atlas_file) # Default slice views are "coronal","axial","sagittal"
  return atlas

# Images that we want to compare - they must be in the same space, size
def get_images():
  image1 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/2mm16_zstat1_1.nii"
  image2 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/2mm16_zstat3_1.nii"
  return [image1,image2]

# Generate thresholds
def generate_thresholds():
  thresholds = []
  for ii in range(0,4):
    thresholds = thresholds + [(float(x) * 0.01)+ii for x in range(0,100)]
  return thresholds

# Test interface output with images thresholded at particular value
def run_scatterplot_compare_threshold(images,image_names,threshold,atlas=None,reference_mask=None,browser_view=False):
  # Threshold the images
  thresholded_images = []
  for image in images:
    mr = nibabel.load(image)
    thresholded_images.append(threshold_abs(mr,threshold))

  # Report overlap of voxels
  pdmask = make_binary_deletion_mask(thresholded_images)
  overlapping_voxels = len(numpy.where(pdmask==1)[0])
  print "%s overlapping voxels at threshold %s" %(overlapping_voxels,threshold)

  # Generate the html_snippet
  if reference_mask==None:
    html_snippet,data_table = compare.scatterplot_compare(images=thresholded_images,image_names=image_names,atlas=atlas,software="FSL",corr="pearson") 
  else: 
    html_snippet,data_table = compare.scatterplot_compare(images=thresholded_images,image_names=image_names,atlas=atlas,software="FSL",corr="pearson",reference_mask=reference_mask) 

  # If we want to view in the browser
  if browser_view == True:
    view(html_snippet)

  return html_snippet,data_table,thresholded_images, overlapping_voxels


# Test scatterplot compare correlations against Neurovault with different thresholds
def run_scatterplot_compare_correlation(images,image_names,threshold,atlas=None,reference_mask=None,browser_view=False):
  
  # Get the html snippet and data table (with regional correlations)
  html_snippet,data_table,thresholded_images,overlap = run_scatterplot_compare_threshold(images=images,image_names=image_names,threshold=threshold,atlas=atlas,reference_mask=reference_mask,browser_view=browser_view)
  
  # Format the regional correlations into a smaller table
  scores = data_table.loc[:,["ATLAS_LABELS","ATLAS_CORR"]]
  scores = scores.drop_duplicates()
  df = pandas.DataFrame(scores)
  df["threshold"] = threshold
  df["overlapping_voxels"] = overlap

  # Calculate a whole brain correlation using same NeuroVault function
  nv_correlation = calculate_voxelwise_pearson_similarity(thresholded_images[0], thresholded_images[1])

  # Calculate a whole brain correlation with same procedure as in pybraincompare
  pbc_correlation = calculate_pybraincompare_pearson(thresholded_images)
  return df,nv_correlation,pbc_correlation

# Calculate a whole brain correlation with same procedure as in pybraincompare
def calculate_pybraincompare_pearson(images):
  pdmask = make_binary_deletion_mask(images)
  pdmask = nibabel.Nifti1Image(pdmask,header=images[0].get_header(),affine=images[0].get_affine())
  masked = do_mask(images=images,mask=pdmask)
  masked = pandas.DataFrame(numpy.transpose(masked))
  pbc_correlation = do_pairwise_correlation(masked[0],masked[1],corr_type="pearson")
  return pbc_correlation["No Label"]

# General running function for some set of images and an atlas
def run_scatterplot_compare(images,image_names,atlas,atlas_rendering=None,reference_mask=None):
  if reference_mask == None:
    html_snippet,data_table = compare.scatterplot_compare(images=images,image_names=image_names,atlas=atlas,atlas_rendering=atlas_rendering,software="FSL",corr="pearson") 
  else:
    html_snippet,data_table = compare.scatterplot_compare(images=images,image_names=image_names,atlas=atlas,atlas_rendering=atlas_rendering,software="FSL",corr="pearson",reference_mask=reference_mask)  

# Threshold the image
def threshold_abs(image1,thresh):
  data = image1.get_data()
  tmp = numpy.zeros(image1.shape)  
  tmp[numpy.abs(data) >= thresh] = data[numpy.abs(data) >= thresh]  
  new_image = nibabel.Nifti1Image(tmp,affine = image1.get_affine(),header=image1.get_header())
  return new_image
