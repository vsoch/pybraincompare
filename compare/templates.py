import os
from futils import get_package_dir
import pandas

def get_template(html_name,data_frame):
  template = read_template(html_name)
  replacements = data_frame.columns
  for rep in replacements:
    dat = data_frame[rep]
    dat = [str(d) for d in dat]
    dat = ",".join(dat)
    template = [t.replace(rep,dat) for t in template]
  return template

def read_template(html_name):

  # Get package directory
  ppwd = get_package_dir()  
  html_name = html_name + ".html"
  template_file = os.path.join(ppwd,'template', html_name)
  return open(template_file,"r").readlines()
