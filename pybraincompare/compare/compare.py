'''
compare.py: part of pybraincompare package
Functions to perform and visualize image comparisons

'''
from pybraincompare.template.templates import get_template, add_string, add_javascript_function
from pybraincompare.template.visual import calculate_similarity_search, show_brainglass_interface
from mrutils import get_standard_mask, do_mask, make_binary_deletion_mask, resample_images_ref, get_nii_obj
from pybraincompare.mr.datasets import get_mni_atlas
from maths import calculate_correlation
import numpy as np
import collections
import pandas
import nibabel
import os

# Visual comparison with scatterplot
'''scatterplot_compare: Generate a d3 scatterplot for two registered, standardized images.
- images: list with full paths to image 1, image 2, or nibabel nifti1 images. Must be in MNI space [required]
- software: FSL or FREESURFER [default FSL]
- atlas: a pybraincompare "atlas" object, will be rendered in vis and color data points [default None]
- atlas_rendering: a pybraincompare "atlas" object for rending svg (should be higher res, 2mm) [default None]
- custom: custom dictionary of {"TEMPLATE_IDS":,"text to substitute"} [default None]
- corr: regional correlation type to include [default pearson]
- reference: if a different standard mask is desired to resample images to [default None]
'''
def scatterplot_compare(images,image_names,software="FSL",atlas=None,atlas_rendering=None,
                        custom=None,corr_type="pearson",reference=None,resample_dim=[8,8,8]):

  # Ensure that images are nibabel Nifti1Image objects
  if isinstance(images,str): images = [images]
  images_nii = get_nii_obj(images)

  # Resample to reference
  if reference == None:
    reference = get_standard_mask(software)
  images_resamp, reference_resamp = resample_images_ref(images = images_nii,
                                                        reference=reference,
                                                        interpolation="continuous",
                                                        resample_dim=resample_dim)
    
  # Prepare pairwise deletion mask to apply to data
  pdmask = make_binary_deletion_mask(images_resamp)
  pdmask = nibabel.Nifti1Image(pdmask,header=images_resamp[0].get_header(),
                               affine=images_resamp[0].get_affine())

  # If the user doesn't specify a custom atlas, we use MNI 152 2mm for visual, 8mm for regions
  if atlas == None:
    atlases = get_mni_atlas(["2","8"]) # 2mm (for svg) and 8mm (for roi)
    atlas2mm = atlases["2"]
    atlas = atlases["8"]
  else:
    if atlas_rendering == None: atlas2mm = atlas # we render whatever the user provided
    else: atlas2mm = atlas_rendering 

  # Only do calculations if we have overlapping regions
  if not (pdmask.get_data() == 0).all():
    masked = calculate_correlation(images=images_resamp,mask=pdmask,
                                         atlas=atlas,corr_type=corr_type)

    # Here we return only regions with 3+ points
    counts =  dict(collections.Counter(masked.ATLAS_LABELS.tolist()))
    regions_to_eliminate = [x for x,y in counts.iteritems() if y < 3]
    masked = masked[masked.ATLAS_LABELS.isin(regions_to_eliminate)==False]
    
    # Get template, show error message if there are no surviving correlations
    template = get_template("scatter_atlas",masked)
    if masked.shape[0] == 0:
      template = add_javascript_function('d3.selectAll("svg.svglegend").remove();\nd3.selectAll("svg.svgplot").remove();\nd3.selectAll("pybrain").append("div").attr("class","alert alert-danger").attr("role","alert").attr("style","width:90%; margin-top:30px").text("Not enough overlap in regions to calculate correlations!")',template)
    else:
      if custom:  # Add user custom text
        template = add_string(custom,template)
      # These will only fill in if were not filled in as custom
      template = add_string({"IMAGE_1":image_names[0],
                             "IMAGE_2":image_names[1],
                             "IMAGE_1_LINK":"#",
                             "IMAGE_2_LINK":"#"},template)

    # Add SVGs, we render the 2mm atlas that looks nicer
    template = add_string(atlas2mm.svg,template)      
    
  # If there are not overlapping voxels in the pdmask
  else:
    masked = pandas.DataFrame(columns=["INPUT_DATA_ONE","INPUT_DATA_TWO","ATLAS_DATA",
                                       "ATLAS_LABELS","ATLAS_CORR","ATLAS_COLORS"])
    template = get_template("scatter_atlas",masked)  
    template = add_string(atlas2mm.svg,template)      
    template = add_javascript_function('d3.selectAll("svg.svglegend").remove();\nd3.selectAll("svg.svgplot").remove();\nd3.selectAll("pybrain").append("div").attr("class","alert alert-danger").attr("role","alert").attr("style","width:90%; margin-top:30px").text("Not enough overlap in regions to calculate correlations!")',template)
  
  # Return complete html and raw data
  return template,masked  

# Show images in brain glass interface and sort by tags [IN DEV]
"""brainglass_interface: interface to see most similar brain images.
tags: must be a list of lists, one for each image, with tag categories
"""
def brainglass_interface(mr_paths,software="FREESURFER",voxdim=[8,8,8],
                         tags=None,image_paths=None):

  if tags:
    if len(tags) != len(mr_paths):
      print "ERROR: Number of tags must be equal to number of images!"

  if image_paths:
    if len(image_paths) != len(mr_paths):
      print "ERROR: Number of image files provided must be equal to number of images!"

  # Get the reference brain mask
  reference = get_standard_mask(software)
  masked = do_mask(images=mr_paths,mask=reference,resample_dim=voxdim)
  masked = pandas.DataFrame(np.transpose(masked))
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
def similarity_search(image_scores,tags,png_paths,query_png,query_id,button_url,image_url,
                     image_ids,max_results=100,absolute_value=True,top_text=None,bottom_text=None):

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
