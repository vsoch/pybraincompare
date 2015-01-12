import os
import tempfile
import shutil
import contextlib
import futils

# Get the directory of the package
def get_package_dir():
   return os.path.abspath(os.path.join(os.path.dirname(futils.__file__)))

# Make temporary directory
@contextlib.contextmanager
def make_tmp_folder():
  temp_dir = tempfile.mkdtemp()
  yield temp_dir
  shutil.rmtree(temp_dir)

# Filename
def get_name(path):
  return os.path.split(path)[1].split(".")[0]
