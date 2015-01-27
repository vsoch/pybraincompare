# Functions for visualization parameters
from template.futils import make_tmp_folder, make_png_paths, unwrap_list_unique
from nilearn.plotting import plot_glass_brain
from template.templates import add_string
import matplotlib.pyplot as plt
import numpy as np
import random
import webbrowser

'''View code in temporary browser!'''
def view(html_snippet):
  with make_tmp_folder() as tmp_dir:  
    # Write to temporary file
    tmp_file = "%s/pycompare.html" %(tmp_dir)
    internal_view(html_snippet,tmp_file)

'''Internal view function'''
def internal_view(html_snippet,tmp_file):
  html_file = open(tmp_file,'wb')
  html_file.writelines(html_snippet)
  html_file.close()
  url = 'file://%s' %(tmp_file)
  webbrowser.open_new_tab(url)
  raw_input("Press Enter to finish...")

'''Generate N random colors'''
def random_colors(N):
  colors = []
  for x in range(0,N):
    r = lambda: random.randint(0,255)
    colors.append('#%02X%02X%02X' % (r(),r(),r()))
  return colors

def peterson_roi_labels(colors=True):
  color_labels = ["Default","Second-Dorsal-Attention","Ventral-Attention-Language","Second-Visual","Frontal-Parietal","Somatomotor","none","Parietal-Episodic-Retrieval","Parieto-Occipital","Cingulo-opercular","Salience","Frontal-Parietal-Other","First-Dorsal-Attention","First-Visual-V1+","Subcortical"]
  colors = ["#ff2700","#d6add6","#007d7d","#393FAC","#FFFB00","#00ffff","94CD54","#CC0066","#003eff","#fbfbda","#822082","#000000","#c46b8b","#00f700","#94cd54","#CC0066"]
  if not colors: return color_labels
  else: return [colors,color_labels]

def get_colors(N,color_format="decimal"):
  # color scale chosen manually that I like :)
  colors = [[122,197,205],[71,60,139],[255,99,71],[118,238,0],[100,149,237],[255,127,36],[139,0,0],[255,48,48],[34,139,34],[0,206,209],[160,32,240],[238,201,0],[89,89,89],[238,18,137],[205,179,139],[255,0,0]]
  if color_format == "hex":
    colors = ["#7AC5CD","#473C8B","#FF6347","#76EE00","#6495ED","#FF7F24","#8B0000","#FF3030","#228B22","#00CED1","#A020F0","#EEC900","#595959","#EE1289","#CDB38B","#FF0000"]
  elif color_format == "decimal":
    colors = [[round(x/255.0,1) for x in c] for c in colors ]
  else:   
    print "%s is not a valid format." %(color_format)
    return

  if N <= len(colors):  
    colors = colors[0:N]
    return colors
  else:
    print "Current colorscale only has %s colors! Add more!" %(len(colors))

"""Make glassbrain image, optional save image to png file (not vector)"""
def make_glassbrain_image(nifti_file,png_img_file=None):
  nifti_file = str(nifti_file)
  glass_brain = plot_glass_brain(nifti_file)
  if png_img_file:    
    glass_brain.savefig(png_img_file)
  plt.close()
  return glass_brain

"""Get svg html from matplotlib figures (eg, glass brain images)"""
def get_svg_html(mpl_figures):
  svg_images = []
  with make_tmp_folder() as tmp_dir:  
    for fig in mpl_figures:
      tmp_svg = "%s/mplfig.svg" %(tmp_dir)
      fig.savefig(tmp_svg)
      fig_data = open(tmp_svg,"rb").readlines()
      svg_images.append(fig_data)
  return svg_images

"""Generate temporary web interface to show brainglass images"""
def show_brainglass_interface(template,tags,mr_files,image_paths=None):
  with make_tmp_folder() as tmp_dir:  

    # If we need to make the image paths from the mr_files
    if not image_paths: image_paths = make_png_paths(mr_files)

    # Get the unique tags
    all_tags = unwrap_list_unique(tags)
    placeholders = dict()
    for tag in all_tags: placeholders[tag] = tag.replace(" ","")

    # Create portfolio
    portfolio = create_glassbrain_portfolio(image_paths,all_tags,placeholders)
    html_snippet = add_string({"SIMILARITY_PORTFOLIO":portfolio},template)
    tmp_file = "%s/similarity_search.html" %(tmp_dir)
    internal_view(html_snippet,tmp_file)

"""Generate web interface for similarity search
Future version will generate on the fly and use "internal_show"
template: html template (similarity_search)
corr_df: matrix of correlation values for images, with "png" column corresponding to image paths, "tags" corresponding to image tags. Column and row names should be image id.
query: image png (must be in "png" column) that the others will be compared to
button_url: prefix of url that the "compare" button will link to. format will be prefix/[query_id]/[other_id]
image_url: prefix of the url that the "view" button will link to. format will be prefix/[other_id]
max_results: maximum number of results to return
absolute_value: return absolute value of score (default=True)
"""
def show_similarity_search(template,query,corr_df,button_url,image_url,max_results,absolute_value,image_names):
  #if not image_paths: image_paths = make_png_paths(mr_files)
  query_row = corr_df[corr_df["png"] == query]
  query_id = query_row.index[0]
    
  # Sort based on (absolute value of) similarity score
  if absolute_value: 
    query_similar = corr_df[query_id].abs()
    query_similar.sort(ascending=False)
    query_similar = corr_df.loc[query_similar.index]
  else: query_similar = corr_df.sort(columns=query_id,ascending=False)
  
  # Remove the query image, and cut down to 100 results
  query_similar = query_similar[query_similar.index != query_id]
  if query_similar.shape[0] > max_results: query_similar = query_similar[0:max_results]

  # Get the unique tags
  all_tags = unwrap_list_unique(list(query_similar["tags"]))
  placeholders = dict()
  for tag in all_tags: placeholders[tag] = tag.replace(" ","")
    
  #TODO: if we remove columns for other images (so keep query, tags png)(does it speed up?)

  # Create custom urls
  button_urls = ["%s/%s/%s" %(button_url,query_id,x) for x in query_similar.index.tolist()]
  image_urls = ["%s/%s" %(image_url,x) for x in query_similar.index.tolist()]

  # Create portfolio with images and tags
  scores = np.round(query_similar[query_id].values,2)
  png_images = query_similar["png"].tolist()
  tags_list = query_similar["tags"].tolist()
  portfolio = create_glassbrain_portfolio(image_paths=png_images,all_tags=all_tags,tags=tags_list,placeholders=placeholders,values=scores,button_urls=button_urls,image_urls=image_urls,image_names=image_names)
  template = add_string({"SIMILARITY_PORTFOLIO":portfolio},template)
  html_snippet = add_string({"QUERY_IMAGE":query},template)
  return html_snippet


'''Base brainglass portfolio for image comparison or brainglass interface standalone'''
def create_glassbrain_portfolio(image_paths,all_tags,tags,placeholders,values=None,button_urls=None,image_urls=None,image_names=None):
    # Create portfolio filters
    portfolio_filters = '<div class="row"><div class="col-md-6" style="padding-left:20px"><ul class="portfolio-filter">\n<li><a class="btn btn-default active" href="#" data-filter="*">All</a></li>'     
    for t in range(0,len(all_tags)):
      tag = all_tags[t]; placeholder = placeholders[tag]      
      portfolio_filters = '%s<li><a class="btn btn-default" href="#" data-filter=".%s">%s</a></li>\n' %(portfolio_filters,placeholder,tag) 
    portfolio_filters = '%s</ul><!--/#portfolio-filter--></div><div class="col-md-6">\n' %(portfolio_filters)
    portfolio_filters = '%s<img class = "query_image" src="[QUERY_IMAGE]"/></div></div>' %(portfolio_filters)

    # Create portfolio items
    portfolio_items = '<ul class="portfolio-items col-3">'
    for i in range(0,len(image_paths)):
      image = image_paths[i]    
      portfolio_items = '%s<li class="portfolio-item ' %(portfolio_items) 
      image_tags = tags[i]
      if image_urls != None: image_url = image_urls[i]
      else: image_url = image
      if image_names != None: image_name = "[%s]" %(image_names[i])
      else: image_name = ""
      if values != None: value = values[i]
      else: value = image
      if button_urls != None: button_url = button_urls[i]
      else: button_url = image
      for it in image_tags:
        portfolio_items = '%s %s ' %(portfolio_items,placeholders[it])
      portfolio_items = '%s">\n<div class="item-inner">\n<img src="%s" alt="">\n' %(portfolio_items,image)
      portfolio_items = '%s\n<h5>Score: %s <span style="color:#FF8C00;">%s</span></h5>\n<div class="overlay"><a class="preview btn btn-danger" href="%s">compare</i></a><a class="preview btn btn-success" href="%s">view</i></a></div></div></li><!--/.portfolio-item-->' %(portfolio_items,value,image_name,button_url,image_url)
    portfolio_items = '%s\n</ul>' %(portfolio_items)                

    portfolio = '%s%s' %(portfolio_filters,portfolio_items)
    return portfolio
