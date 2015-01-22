# Functions for visualization parameters
from template.futils import make_tmp_folder
from nilearn.plotting import plot_glass_brain
from template.templates import add_string
import matplotlib.pyplot as plt
import numpy as np
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

"""Generate temporary web interface for similarity search"""
def show_similarity_search(template,tags,mr_files,image_paths=None):
  with make_tmp_folder() as tmp_dir:  

    # If we need to make the image paths from the mr_files
    if not image_paths:
      image_paths = []
      for i in range(0,len(mr_files)):
        image = mr_files[i]
        tmp_svg = "%s/tmpbrain%s.png" %(tmp_dir,i)
        make_glassbrain_image(image,tmp_svg)
        image_paths.append(tmp_svg)

    # Get the unique tags
    all_tags = []
    for taglist in tags:
      all_tags = all_tags + [tag for tag in taglist]
    all_tags = list(np.unique(all_tags))
    placeholders = dict()
    for tag in all_tags: placeholders[tag] = tag.replace(" ","")

    # Create portfolio filters
    portfolio_filters = '<ul class="portfolio-filter">\n<li><a class="btn btn-default active" href="#" data-filter="*">All</a></li>'     
    for t in range(0,len(all_tags)):
      tag = all_tags[t]; placeholder = placeholders[tag]      
      portfolio_filters = '%s<li><a class="btn btn-default" href="#" data-filter=".%s">%s</a></li>\n' %(portfolio_filters,placeholder,tag) 
    portfolio_filters = '%s</ul><!--/#portfolio-filter-->\n' %(portfolio_filters)

    # Create portfolio items
    portfolio_items = '<ul class="portfolio-items col-3">'
    for i in range(0,len(image_paths)):
      image = image_paths[i]    
      portfolio_items = '%s<li class="portfolio-item ' %(portfolio_items) 
      image_tags = tags[i]
      for it in image_tags:
        portfolio_items = '%s %s ' %(portfolio_items,placeholders[it])
      portfolio_items = '%s">\n<div class="item-inner">\n<img src="%s" alt="">\n' %(portfolio_items,image)
      portfolio_items = '%s\n<h5>%s</h5>\n<div class="overlay"><a class="preview btn btn-danger" href="%s"><i class="icon-eye-open"></i></a></div></div></li><!--/.portfolio-item-->' %(portfolio_items,image,image)
    portfolio_items = '%s\n</ul>' %(portfolio_items)                

    # Add both to template
    portfolio = '%s%s' %(portfolio_filters,portfolio_items)
    html_snippet = add_string({"SIMILARITY_PORTFOLIO":portfolio},template)
    tmp_file = "%s/similarity_search.html" %(tmp_dir)
    internal_view(html_snippet,tmp_file)
