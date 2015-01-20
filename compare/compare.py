import nibabel
from mrutils import get_standard_mask, do_mask
from template.templates import get_template, add_string
from template.futils import get_name
from template.visual import make_glassbrain_image
from maths import do_pairwise_correlation, do_multi_correlation
import pandas
import numpy
import os
import atlas

# Unbiased visual comparison with scatterplot
'''scatterplot_compare: Generate a d3 scatterplot for two registered, standardized images.
- image1: full path to image 1, must be in MNI space [required]
- image2: full path to image 2, must be in MNI space [required]
- software: FSL or FREESURFER, currently FREESURFER is better supported [default FSL]
- voxdim: dimension to resample atlas and images into [default [8,8,8]]
- atlas: a pybraincompare "atlas" object, will be rendered in vis and color data points [default None]
- corr: regional correlation type to include [default None]
- custom: custom dictionary of {"TEMPLATE_IDS":,"text to substitute"} [default None]
'''
def scatterplot_compare(image1,image2,software="FSL",voxdim=[8,8,8],atlas=None,corr=None,custom=None):

  # Get the reference brain mask
  reference = get_standard_mask(software)
  masked = do_mask(images=[image1,image2],mask=reference,resample_dim=voxdim)
  masked = pandas.DataFrame(numpy.transpose(masked))

  if atlas:
    masked_atlas = do_mask(images = atlas.file,mask=reference,resample_dim=voxdim,interpolation="nearest")
    masked["ATLAS_DATA"] = numpy.transpose(masked_atlas)
    # Prepare label (names)
    labels = ['"%s"' %(atlas.labels[str(int(x))].label) for x in masked_atlas[0]]
    masked["ATLAS_LABELS"] = labels
    # Add correlation values if user wants to do pearson correlation
    if corr:
      corrs = do_pairwise_correlation(masked[0],masked[1],atlas_vector=masked["ATLAS_LABELS"])
      correlations = [corrs[x] for x in masked["ATLAS_LABELS"]]
    else: correlations = ["" for x in masked["ATLAS_LABELS"]]
    masked["ATLAS_CORR"] = correlations
    # Prepare colors - value of 0 == no label or just empty space, they are equivalent
    colors = ['"%s"' %(atlas.color_lookup[x.replace('"',"")]) for x in labels]
    masked["ATLAS_COLORS"] = colors
    # The column names MUST correspond to the replacement text in the file
    masked.columns = ["INPUT_DATA_ONE","INPUT_DATA_TWO","ATLAS_DATA","ATLAS_LABELS","ATLAS_CORR","ATLAS_COLORS"]
    # Get template
    template = get_template("scatter_atlas",masked)
    # Add user custom text (right now only would be image labels)
    if custom:
      template = add_string(custom,template)
    # Add SVGs, eg atlas_key["coronal"] replaces [coronal]
    template = add_string(atlas.svg,template)
      
    # Finally, add image names
    template = add_string({"image 1":get_name(image1),"image 2":get_name(image2)},template)
  else:
    masked.columns = ["INPUT_DATA_ONE","INPUT_DATA_TWO"]
    template = get_template("scatter",masked)
  
  # Return complete html and raw data
  return template,masked


# Similarity search interface for multiple images
def similarity_search(image_paths,software="FREESURFER",voxdim=[8,8,8],corr="pearson"):

  # Get the reference brain mask
  reference = get_standard_mask(software)
  masked = do_mask(images=image_paths,mask=reference,resample_dim=voxdim)
  masked = pandas.DataFrame(numpy.transpose(masked))
  masked.columns = image_paths
  # Pairwise comparison matrix
  similarity_matrix = do_multi_correlation(masked,corr)
  # Generate glass brain images
  glass_brains = []
  for image in image_paths:
    glass_brains.append(make_glassbrain_image(image))
  

