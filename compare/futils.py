import os
import tempfile
import shutil
import contextlib
import compare

# Make temporary directory
@contextlib.contextmanager
def make_tmp_folder():
  temp_dir = tempfile.mkdtemp()
  yield temp_dir
  shutil.rmtree(temp_dir)

# Get the directory of the package
def get_package_dir():
   return os.path.abspath(os.path.join(os.path.dirname(compare.__file__)))

# Filename
def get_name(path):
  return os.path.split(path)[1]
