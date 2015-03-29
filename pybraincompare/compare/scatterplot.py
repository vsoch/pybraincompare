'''
scatterplot.py: part of pybraincompare package
Functions to perform and create scatterplot comparisons

'''
from pybraincompare.template.templates import get_template, add_string, add_javascript_function
from mrutils import get_standard_mask, make_binary_deletion_mask, resample_images_ref, get_nii_obj
from pybraincompare.mr.datasets import get_mni_atlas
from maths import calculate_correlation, calculate_atlas_correlation
import numpy as np
import collections
import pandas
import nibabel
import os

# SCATTERPLOT COMPARISON #########################################################################################
'''A scatterplot comparison will compare two images by way of a scatterplot, and color points
based on an anatomical (MNI) atlas
'''

'''scatterplot_compare_vector: Generate a d3 scatterplot with all arguments as vectors to outputs html with
the generated d3 plot. Atlas rendering object (atlas) is required for svg data
'''
def scatterplot_compare_vector(image_vector1,image_vector2,image_names,atlas,atlas_vector,
                               atlas_labels,atlas_colors,custom=None,corr_type="pearson",subsample_every=None):

  if len(image_vector1) == len(image_vector2) == len(atlas_vector) == len(atlas_labels) == len(atlas_colors):
    if subsample_every != None:
      sample_index = np.arange(0,len(image_vector1),int(subsample_every))
      image_vector1 = np.array(image_vector1)[sample_index]
      image_vector2 = np.array(image_vector2)[sample_index]
      atlas_vector = np.array(atlas_vector)[sample_index]
      atlas_labels = np.array(atlas_labels)[sample_index]
      atlas_colors = np.array(atlas_colors)[sample_index]
      
    corrs_df = calculate_atlas_correlation(image_vector1,image_vector2,atlas_vector,atlas_labels,
                                atlas_colors,corr_type="pearson",summary=False)
    error = None
  else:
    error = "Lengths of image vectors, atlas vector, atlas labels, and color labels are not equal."

  # Here are all the string elements to add
  elements = [atlas.svg,custom,{"IMAGE_1":image_names[0]},
                               {"IMAGE_2":image_names[1]},
                               {"IMAGE_1_LINK":"#"},
                               {"IMAGE_2_LINK":"#"}]
  if custom == None: elements.pop(1)

  # If we have an error, generate empty dataframe
  if error != None:
    corrs_df = pandas.DataFrame(columns=["INPUT_DATA_ONE","INPUT_DATA_TWO","ATLAS_DATA",
                                       "ATLAS_LABELS","ATLAS_CORR","ATLAS_COLORS"])

  # Prepare template from correlation data frame
  template = make_scatterplot_interface(corrs_df,error=error,elements=elements)
      
  # Return complete html and raw data
  return template,corrs_df  


'''scatterplot_compare: Generate a d3 scatterplot for two registered, standardized images.
- images: list with full paths to image 1, image 2, or nibabel nifti1 images. Must be in MNI space [required]
- software: FSL or FREESURFER [default FSL]
- atlas: a pybraincompare "atlas" object, will be rendered in vis and color data points [default None]
- atlas_rendering: a pybraincompare "atlas" object for rending svg (should be higher res, 2mm) [default None]
- custom: custom dictionary of {"TEMPLATE_IDS":,"text to substitute"} [default None]
- corr: regional correlation type to include [default pearson]
- reference: if a different standard mask is desired to resample images to [default None]
- resample_dim: the dimension to resample the reference, and then images, to
'''
def scatterplot_compare(images,image_names,software="FSL",atlas=None,atlas_rendering=None,
                        custom=None,corr_type="pearson",reference=None,resample_dim=[8,8,8]):

  # Ensure that images are nibabel Nifti1Image objects
  if isinstance(images,str): images = [images]
  images_nii = get_nii_obj(images)

  # Resample to reference
  if reference == None:
    reference = get_standard_mask(software)
  images_resamp, reference_resamp = resample_images_ref(images=images_nii,
                                                        reference=reference,
                                                        interpolation="continuous",
                                                        resample_dim=resample_dim)
    
  # Prepare pairwise deletion mask to apply to data
  pdmask = make_binary_deletion_mask(images_resamp)
  pdmask = nibabel.Nifti1Image(pdmask,header=images_resamp[0].get_header(),
                               affine=images_resamp[0].get_affine())

  # Get atlas to apply to data (atlas) and to render in d3 (2mm)
  atlas, atlas2mm = get_atlas_objects(atlas,atlas_rendering)

  # We will not render the atlas if there is an error along the way
  error = None

  # Only do calculations if we have overlapping regions based on pdmask
  if not (pdmask.get_data() == 0).all():
    corr_df = calculate_correlation(images=images_resamp,mask=pdmask,
                                   atlas=atlas,corr_type=corr_type)
    # If calculate correlation returns nan, no surviving regional correlations 
    if not isinstance(corr_df,pandas.DataFrame):
      error = "No surviving correlations with atlas!"

  else: # No overlapping voxels in the pdmask
    error = "Not enough overlap in union of images!"

  # Here are all the string elements to add
  elements = [atlas2mm.svg,custom,{"IMAGE_1":image_names[0]},
                                    {"IMAGE_2":image_names[1]},
                                    {"IMAGE_1_LINK":"#"},
                                    {"IMAGE_2_LINK":"#"}]
  if custom == None: elements.pop(1)

  # If we have an error, generate empty dataframe
  if error != None:
    corr_df = pandas.DataFrame(columns=["INPUT_DATA_ONE","INPUT_DATA_TWO","ATLAS_DATA",
                                       "ATLAS_LABELS","ATLAS_CORR","ATLAS_COLORS"])

  # Prepare template from correlation data frame
  template = make_scatterplot_interface(corr_df,error=error,elements=elements)
      
  # Return complete html and raw data
  return template,corr_df  


# Function to combine data with scatterplot template, return template html
'''
corr_df: a pandas data frame with INPUT_DATA_ONE,INPUT_DATA_TWO, ATLAS_DATA,ATLAS_LABELS,ATLAS_CORR,ATLAS_COLORS
elements: a list of string elements to add to the template, each element is a dictionary with:
  key corresponding to tag to replace in template
  value corresponding to the text that will replace the tag
error: if specified, will replace scatterplot with error to show user
'''
def make_scatterplot_interface(corr_df,elements,error=None):

  # We want to return only regions with 3+ points
  counts =  dict(collections.Counter(corr_df.ATLAS_LABELS.tolist()))
  regions_to_eliminate = [x for x,y in counts.iteritems() if y < 3]
  corr_df = corr_df[corr_df.ATLAS_LABELS.isin(regions_to_eliminate)==False]

  # Error: If all regions have fewer than 3 values
  if corr_df.shape[0] == 0:
    error = "Fewer than three values in all regions shared by images!"
  
  template = get_template("scatter_atlas",corr_df)  
  for element in elements:
    template = add_string(element,template)      

  if error != None:
    template = scatterplot_compare_error(template,error)

  return template


# Add message to scatterplot compare that calculation was not possible
def scatterplot_compare_error(template,specific_error):
  template = add_javascript_function('d3.selectAll("svg.svglegend").remove();\nd3.selectAll("svg.svgplot").remove();\nd3.selectAll("pybrain").append("div").attr("class","alert alert-danger").attr("role","alert").attr("style","width:90%; margin-top:30px").text("Scatterplot Comparison Correlations Not Possible: %s!")' %(specific_error),template)
  return template

# Get atlas objects based on what user has provided
'''return atlas for rendering (2mm) and atlas for applying to images (atlas) based
on what is provided by the user:
- if user doesn't specify any atlas, MNI 152 2mm is used for visual, 8mm for regions
- if user specifies an atlas, but not a rendering, the atlas is used as the rendering
- if user specifies an atlas, and a rendering, the rendering is rendered
'''
def get_atlas_objects(atlas,atlas_rendering):

  # If the user doesn't specify a custom atlas, we use MNI 152 2mm for visual, 8mm for regions
  if atlas == None:
    atlases = get_mni_atlas(["2","8"]) # 2mm (for svg) and 8mm (for roi)
    atlas2mm = atlases["2"]
    atlas = atlases["8"]
  else:
    if atlas_rendering == None: atlas2mm = atlas # we render whatever the user provided
    else: atlas2mm = atlas_rendering 

  return atlas,atlas2mm
