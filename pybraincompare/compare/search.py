'''
search.py: part of pybraincompare package
Generate search interfaces to compare images

'''
from pybraincompare.template.templates import get_template, add_string, add_javascript_function, remove_resources
from mrutils import get_standard_mask, do_mask, make_binary_deletion_mask, resample_images_ref, get_nii_obj
from pybraincompare.template.futils import unwrap_list_unique
from pybraincompare.mr.datasets import get_mni_atlas
from maths import calculate_correlation
import numpy as np
import collections
import pandas
import nibabel
import os


# SIMILARITY SEARCH ###############################################################################################

# Search interface to show images most similar to a query
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
remove_scripts: list of strings corresponding to js or css template tags to remove [OPTIONAL]
"""
def similarity_search(image_scores,tags,png_paths,query_png,query_id,button_url,image_url,image_ids,
                     max_results=100,absolute_value=True,top_text=None,bottom_text=None,
                     container_width=940,remove_scripts=None):

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

  html_snippet = calculate_similarity_search(template=template,corr_df=corr_df,query_png=query_png,
                                       query_id=query_id,button_url=button_url,image_url=image_url,
                                       max_results=max_results,absolute_value=absolute_value,
                                       container_width=container_width)

  if remove_scripts != None:
    if isinstance(remove_scripts,str): remove_scripts = [remove_scripts]
    html_snippet = remove_resources(html_snippet,script_names=remove_scripts)
  return html_snippet


"""Generate web interface for similarity search
template: html template (similarity_search)
query_png: image png (must be in "png" column) that the others will be compared to
query_id: id of the query image, to look up in corr_df
corr_df: matrix of correlation values for images, with "png" column corresponding to image paths, "tags" corresponding to 
button_url: prefix of url that the "compare" button will link to. format will be prefix/[query_id]/[other_id]
image_url: prefix of the url that the "view" button will link to. format will be prefix/[other_id]
max_results: maximum number of results to return
absolute_value: return absolute value of score (default=True)
responsive: for larger number of returned results: will load images only when scrolled to.
"""

def calculate_similarity_search(template,query_png,query_id,corr_df,button_url,
                                image_url,max_results,absolute_value,container_width,responsive=True):
  """calculate_similarity_search_df starts with pandas data frame to make similarity interface"""
  query_row = corr_df[corr_df["png"] == query_png]
    
  # Sort based on (absolute value of) similarity score
  if absolute_value: 
    query_similar = corr_df["scores"].abs()
    query_similar.sort(ascending=False)
    query_similar = corr_df.loc[query_similar.index]
  else: query_similar = corr_df.sort(columns="scores",ascending=False)
  
  # Remove the query image, and cut down to 100 results
  query_similar = query_similar[query_similar.index != query_id]
  if query_similar.shape[0] > max_results: query_similar = query_similar[0:max_results]

  # Prepare data for show_similarity_search
  image_ids = query_similar.image_ids.tolist()
  all_tags = query_similar.tags.tolist()
  scores = np.round(query_similar.scores.values,2)
  png_images = query_similar.png.tolist()
  top_text = query_similar.top_text.tolist()
  bottom_text = query_similar.bottom_text.tolist()

  # Get the unique tags
  unique_tags = unwrap_list_unique(all_tags)
  placeholders = dict()
  for tag in unique_tags: placeholders[tag] = tag.replace(" ","")

  # Create custom urls
  button_urls = ["%s/%s/%s" %(button_url,query_id,x) for x in image_ids]
  image_urls = ["%s/%s" %(image_url,x) for x in image_ids]

  # Create portfolio with images and tags
  #if responsive == True:
  #    portfolio = create_glassbrain_portfolio_responsive(image_paths=png_images,all_tags=all_tags,unique_tags=unique_tags,
  #                                        placeholders=placeholders,values=scores,button_urls=button_urls,
  #                                        image_urls=image_urls,top_text=top_text,bottom_text=bottom_text)     
  #else:
  portfolio = create_glassbrain_portfolio(image_paths=png_images,all_tags=all_tags,unique_tags=unique_tags,
                                          placeholders=placeholders,values=scores,button_urls=button_urls,
                                          image_urls=image_urls,top_text=top_text,bottom_text=bottom_text)

  elements = {"SIMILARITY_PORTFOLIO":portfolio,"CONTAINER_WIDTH":container_width}
  template = add_string(elements,template)
  html_snippet = add_string({"QUERY_IMAGE":query_png},template)
  return html_snippet


'''Base brainglass portfolio for image comparison or brainglass interface standalone'''
def create_glassbrain_portfolio(image_paths,all_tags,unique_tags,placeholders,values=None,
                                button_urls=None,image_urls=None,top_text=None,bottom_text=None):
    # Create portfolio filters
    portfolio_filters = '<div class="row"><div class="col-md-8" style="padding-left:20px"><ul class="portfolio-filter">\n<li><a class="btn btn-default active" href="#" data-filter="*">All</a></li>'     

    # Get loading message image
    glass_brain_loading = "http://placehold.it/324x128&text=Loading..."

    for t in range(0,len(unique_tags)):
      tag = unique_tags[t]; placeholder = placeholders[tag]      
      portfolio_filters = '%s<li><a class="btn btn-default" href="#" data-filter=".%s">%s</a></li>\n' %(portfolio_filters,placeholder,tag) 
    portfolio_filters = '%s</ul><!--/#portfolio-filter--></div><div>\n' %(portfolio_filters)
    portfolio_filters = '%s<img class = "query_image" src="[QUERY_IMAGE]"/></div></div>' %(portfolio_filters)

    # Create portfolio items
    portfolio_items = '<ul class="portfolio-items col-3">'
    for i in range(0,len(image_paths)):
      image = image_paths[i]    
      portfolio_items = '%s<li class="portfolio-item ' %(portfolio_items) 
      image_tags = all_tags[i]
      if image_urls != None: image_url = image_urls[i]
      else: image_url = image
      if top_text != None: ttext = "%s" %(top_text[i])
      else: ttext = ""
      if bottom_text != None: btext = "%s" %(bottom_text[i])
      else: btext = ""
      if values != None: value = values[i]
      else: value = image
      if button_urls != None: button_url = button_urls[i]
      else: button_url = image
      for it in image_tags:
        portfolio_items = '%s %s ' %(portfolio_items,placeholders[it])
      if i != (len(image_paths)-1):
          portfolio_items = '%s" style="position: absolute; left: 303px; top: 0px;">\n<div class="item-inner">\n<h5><span style="color:#FF8C00; align:right">%s</span></h5>\n<img data-layzr="%s" src="%s" alt="">\n' %(portfolio_items,ttext,image,glass_brain_loading)
          portfolio_items = '%s\n<h5>Score: %s <span style="color:#FF8C00;">%s</span></h5>\n<div class="overlay"><a class="preview btn btn-danger" href="%s">compare</i></a><a class="preview btn btn-success" href="%s">view</i></a></div></div></li><!--/.portfolio-item-->' %(portfolio_items,value,btext,button_url,image_url)
      else:
          portfolio_items = '%s" style="position: absolute; left: 303px; top: 0px;">\n<div class="item-inner">\n<h5><span style="color:#FF8C00; align:right">%s</span></h5>\n<img data-layzr="%s" src="%s" alt="" onload="imgLoaded(this)">\n' %(portfolio_items,ttext,image,glass_brain_loading)
          portfolio_items = '%s\n<h5>Score: %s <span style="color:#FF8C00;">%s</span></h5>\n<div class="overlay"><a class="preview btn btn-danger" href="%s">compare</i></a><a class="preview btn btn-success" href="%s">view</i></a></div></div></li><!--/.portfolio-item-->' %(portfolio_items,value,btext,button_url,image_url)
    portfolio_items = '%s\n</ul>' %(portfolio_items)                
    portfolio = '%s%s' %(portfolio_filters,portfolio_items)
    return portfolio
