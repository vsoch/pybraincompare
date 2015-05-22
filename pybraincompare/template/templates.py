'''
templates.py: part of pybraincompare package
Functions to work with html templates

'''

from futils import get_package_dir
import pandas
import os
import re

def get_template(html_name,data_frame=None):
  template = read_template(html_name)
  if isinstance(data_frame,pandas.core.frame.DataFrame):
    replacements = data_frame.columns
    for rep in replacements:
      dat = data_frame[rep]
      dat = [str(d) for d in dat]
      dat = ",".join(dat)
      template = [t.replace(rep,dat) for t in template]
  return template


# Add code string to end of template
def add_javascript_function(function_code,template):
  template.append("<script>\n%s\n</script>" % (function_code))
  return template

# Remove scripts (css or js) from html_snippet
def remove_resources(html_snippet,script_names):
  expression = re.compile("|".join(script_names))
  filtered_template = [x for x in html_snippet if not expression.search(x)]
  return filtered_template

def save_template(html_snippet,output_file):
  filey = open(output_file,"wb")
  filey.writelines(html_snippet)
  filey.close()

def read_template(html_name):

  # Get package directory
  ppwd = get_package_dir()  
  html_name = html_name + ".html"
  template_file = os.path.join(ppwd,'html', html_name)
  return open(template_file,"r").readlines()

'''Add strings (eg, svg code) to a template - the key of the atlas_svg should correspond to replacement text. eg, svg["coronal"] will replace [coronal] tag in template!'''
def add_string(svg,template):
  # If the number of svgs is != text_substitutions, we add them all to same spot
  for tag,code in svg.iteritems():
    template = [t.replace("[%s]" %(tag),"%s" %(code)) for t in template]
  return template

'''Get an image by name in the img directory'''
def get_image(image_name):
  ppwd = get_package_dir()  
  return os.path.join(ppwd,'img', image_name)
