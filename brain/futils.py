import os
import brain

# Get the directory of the package
def get_package_dir():
   return os.path.abspath(os.path.join(os.path.dirname(brain.__file__),".."))
