'''
compare.py: part of pybraincompare package
Functions to perform and visualize image comparisons

'''

import pandas
import numpy
import os
import atlas
import nibabel
import collections
from template.futils import get_name
from maths import do_pairwise_correlation, do_multi_correlation
from template.templates import get_template, add_string, add_javascript_function
from template.visual import calculate_similarity_search, show_brainglass_interface
from mrutils import get_standard_mask, do_mask, make_binary_deletion_mask, resample_images_ref


# Unbiased visual comparison with scatterplot
'''scatterplot_compare: Generate a d3 scatterplot for two registered, standardized images.
- image1: full path to image 1, must be in MNI space [required]
- image2: full path to image 2, must be in MNI space [required]
- software: FSL or FREESURFER [default FSL]
- voxdim: if images not in same space: dimension to resample atlas and images into [default [8,8,8]]
- atlas: a pybraincompare "atlas" object, will be rendered in vis and color data points [default None]
- corr: regional correlation type to include [default pearson]
- custom: custom dictionary of {"TEMPLATE_IDS":,"text to substitute"} [default None]
'''
def scatterplot_compare(images,software="FSL",voxdim=[8,8,8],atlas=None,custom=None,corr="pearson"):

  # Resample if images not equal sized (this will slow down calculation)
  if isinstance(images,str): images = [images]
  images_resamp = []
  image_names = []
  for i in range(0,len(images)):
    image = images[i]    
    if not isinstance(image,nibabel.nifti1.Nifti1Image): 
      image_names.append(get_name(image))
      image = nibabel.load(image)
    else: image_names.append("image %s" %(i))  
    images_resamp.append(image)

  # Make sure the affines are equivalent
  affines = [mr.get_affine() for mr in images_resamp]
  if not all((x == affines[0]).all() for x in affines):  
    reference = get_standard_mask(software)
    images_resamp, reference_resamp = resample_images_ref(images_resamp,reference,interpolation="continuous")
    
  # Prepare pairwise deletion mask, apply to data
  pdmask = make_binary_deletion_mask(images_resamp)
  pdmask = nibabel.Nifti1Image(pdmask,header=images_resamp[0].get_header(),affine=images_resamp[0].get_affine())
  masked = do_mask(images=images_resamp,mask=pdmask)
  masked = pandas.DataFrame(numpy.transpose(masked))

  # If we are including an atlas, it must also be the same size
  if atlas: 
    atlas_nii = nibabel.load(atlas.file)
    if not (atlas_nii.get_affine() == images_resamp[0].get_affine()).all():  
      atlas_nii, ref_nii = resample_images_ref(atlas.file,images_resamp[0],interpolation="nearest")
    masked_atlas = do_mask(atlas_nii,mask=pdmask)    
    masked["ATLAS_DATA"] = numpy.transpose(masked_atlas)

    # Prepare label (names), correlation values, and colors
    labels = ['"%s"' %(atlas.labels[str(int(x))].label) for x in masked_atlas[0]]
    masked["ATLAS_LABELS"] = labels   
    corrs = do_pairwise_correlation(masked[0],masked[1],atlas_vector=masked["ATLAS_LABELS"],corr_type=corr)
    masked["ATLAS_CORR"] = [corrs[x] for x in masked["ATLAS_LABELS"]]
    masked["ATLAS_COLORS"] = ['"%s"' %(atlas.color_lookup[x.replace('"',"")]) for x in labels]
    masked.columns = ["INPUT_DATA_ONE","INPUT_DATA_TWO","ATLAS_DATA","ATLAS_LABELS","ATLAS_CORR","ATLAS_COLORS"]
    
    # Here we return only regions with 3+ points
    counts =  dict(collections.Counter(masked.ATLAS_LABELS.tolist()))
    regions_to_eliminate = [x for x,y in counts.iteritems() if y < 3]
    masked = masked[masked.ATLAS_LABELS.isin(regions_to_eliminate)==False]
    
    # Get template, show error message if there are no surviving correlations
    template = get_template("scatter_atlas",masked)
    if masked.shape[0] == 0:
      template = add_javascript_function('d3.selectAll("svg.svglegend").remove();\nd3.selectAll("svg.svgplot").remove();\nd3.selectAll("pybrain").append("div").attr("class","alert alert-danger").attr("role","alert").attr("style","width:90%; margin-top:30px").text("Not enough overlap in regions to calculate correlations!")',template)
    else:
      # Add user custom text (right now only would be image labels)
      if custom:
        template = add_string(custom,template)
      # Finally, add image names and links - these names will only fill in if were not filled in for custom above
      template = add_string({"IMAGE_1":image_names[0],"IMAGE_2":image_names[1],"IMAGE_1_LINK":"#","IMAGE_2_LINK":"#"},template)
    # Add SVGs, eg atlas_key["coronal"] replaces [coronal]
    template = add_string(atlas.svg,template)      
  
  # If we don't have an atlas
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
image_scores: list of image scores
tags: a list of lists of tags, one for each image, in same order as data
png_paths: a list of pre-generated png images, one for each image, in same order as data
query_png: full path to query png image. Must be in png_paths
query_id: id of query image, must be in image_ids
button_url: prefix of url that the "compare" button will link to. format will be prefix/[query_id]/[other_id]
image_url: prefix of the url that the "view" button will link to. format will be prefix/[other_id]
image_ids: all image ids that correspond to same order of png paths, tags, and scores
max_results: maximum number of results to return
absolute_value: return absolute value of score (default=True)
top_text: a list of text labels to show on top of images [OPTIONAL]
bottom_text: a list of text labels to show on bottoms of images [OPTIONAL]
"""
def similarity_search(image_scores,tags,png_paths,query_png,query_id,button_url,image_url,image_ids,max_results=100,absolute_value=True,top_text=None,bottom_text=None):

  # Get template
  template = get_template("similarity_search")

  if query_id not in image_ids:
    print "ERROR: Query id must be in list of image ids!"
    return

  if len(tags) != len(png_paths) != len(image_ids):
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
  corr_df["top_text"] = top_text
  corr_df["bottom_text"] = bottom_text
  corr_df.index = image_ids

  return calculate_similarity_search(template=template,corr_df=corr_df,query_png=query_png,
                                       query_id=query_id,button_url=button_url,image_url=image_url,
                                       max_results=max_results,absolute_value=absolute_value)
