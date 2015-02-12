'''
compare.py: part of pybraincompare package
Functions to perform and visualize image comparisons

'''

import pandas
import numpy
import os
import atlas
import nibabel
from template.futils import get_name
from template.templates import get_template, add_string
from maths import do_pairwise_correlation, do_multi_correlation
from mrutils import get_standard_mask, do_mask, make_binary_deletion_mask
from template.visual import calculate_similarity_search, show_brainglass_interface


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

  # Get the reference brain mask, make pairwise deletion mask
  reference = get_standard_mask(software)
  image1_nib = nibabel.load(image1)
  image2_nib = nibabel.load(image2)
  pdmask = make_binary_deletion_mask([image1_nib,image2_nib])
  pdmask = nibabel.Nifti1Image(pdmask,header=image1_nib.get_header(),affine=image1_nib.get_affine())
  masked = do_mask(images=[image1,image2],mask=reference,resample_dim=voxdim,second_mask=pdmask)
  masked = pandas.DataFrame(numpy.transpose(masked))

  if atlas:
    masked_atlas = do_mask(images = atlas.file,mask=reference,resample_dim=voxdim,interpolation="nearest",second_mask=pdmask)
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
      
    # Finally, add image names and links
    template = add_string({"IMAGE_1":get_name(image1),"IMAGE_2":get_name(image2),"IMAGE_1_LINK":"#","IMAGE_2_LINK":"#"},template)
  else:
    masked.columns = ["INPUT_DATA_ONE","INPUT_DATA_TWO"]
    template = get_template("scatter",data_frame=masked)
  
  # Return complete html and raw data
  return template,masked


# Show images in brain glass interface and sort by tags [IN DEV]
"""brainglass_interface: interface to see most similar brain images.
tags: must be a list of lists, one for each image, with tag categories
"""
def brainglass_interface(mr_paths,software="FREESURFER",voxdim=[8,8,8],tags=None,image_paths=None):

  if tags:
    if len(tags) != len(mr_paths):
      print "ERROR: Number of tags must be equal to number of images!"

  if image_paths:
    if len(image_paths) != len(mr_paths):
      print "ERROR: Number of image files provided must be equal to number of images!"

  # Get the reference brain mask
  reference = get_standard_mask(software)
  masked = do_mask(images=mr_paths,mask=reference,resample_dim=voxdim)
  masked = pandas.DataFrame(numpy.transpose(masked))
  masked.columns = mr_paths
  # Get template
  template = get_template("brainglass_interface")
  # Generate temporary interface, if brainglass images don't exist, they will be generated
  show_brainglass_interface(template=template,tags=tags,mr_files=mr_paths,image_paths=image_paths)


# Search interface to show images most similar to a query in database
"""similarity_search: interface to see most similar brain images.
data: pandas series of similarity scores, including the query. Row names should be image ids. column name is query id.
query: image png (must be in "png" column) that the others will be compared to
tags: a list of lists of tags, one for each image, in same order as data
png_paths: a list of pre-generated png images, one for each image, in same order as data
button_url: prefix of url that the "compare" button will link to. format will be prefix/[query_id]/[other_id]
image_url: prefix of the url that the "view" button will link to. format will be prefix/[other_id]
max_results: maximum number of results to return
absolute_value: return absolute value of score (default=True)
image_names: a list of image names to show in interface [OPTIONAL]
"""
def similarity_search(image_scores,tags,png_paths,query_png,query_id,button_url,image_url,image_ids,max_results=100,absolute_value=True,image_names=None):

  # Get template
  template = get_template("similarity_search")

  if query_id not in image_ids:
    print "ERROR: Query id must be in list of image ids!"
    return

  if len(tags) != len(png_paths) != len(image_ids) != data.shape[0]:
    print "ERROR: Number of image paths, tags, number of rows and columns in data frame must be equal"
    return

  if query_png not in png_paths: 
    print "ERROR: Query image png path must be in data frame 'png' paths!" 
    return

  corr_df = pandas.DataFrame() 
  corr_df["png"] = png_paths
  corr_df["tags"] = tags
  corr_df["scores"] = image_scores
  corr_df["image_ids"] = image_ids
  corr_df["image_names"] = image_names
  corr_df.index = image_ids

  return calculate_similarity_search(template=template,corr_df=corr_df,query_png=query_png,
                                       query_id=query_id,button_url=button_url,image_url=image_url,
                                       max_results=max_results,absolute_value=absolute_value)
