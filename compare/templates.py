import os
from futils import get_package_dir

def get_template(html_name,table_file):
  template = read_template(html_name)
  template = [t.replace("INPUT_DATA_PATH",table_file) for t in template]
  return template

def read_template(html_name):

  # Get package directory
  ppwd = get_package_dir()  
  html_name = html_name + ".html"
  template_file = os.path.join(ppwd,'template', html_name)
  return open(template_file,"r").readlines()
