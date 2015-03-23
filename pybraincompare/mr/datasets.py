'''
datasets.py: part of pybraincompare package
Return sets of images or atlas files

'''

import os
import pybraincompare.compare.atlas as Atlas

# Get data directory
def get_data_directory():
  mr_directory = os.path.join(os.path.abspath(os.path.dirname(Atlas.__file__) + "/.."),"mr") 
  return mr_directory

# Return paths to pybraincompare atlas
'''Returns path to MNI atlas in MNI 152 space'''
def get_mni_atlas(voxdims=["2","8"],views=None):
  atlas_directory = get_data_directory()
  atlas_xml = "%s/MNI.xml" %(atlas_directory)
  atlases = dict()
  for dim in voxdims:
    atlas_file = "%s/MNI-maxprob-thr25-%smm.nii" %(atlas_directory,dim)
    if views == None: # return all orthogonal
      atlas = Atlas.atlas(atlas_xml,atlas_file)
    else:
      atlas = Atlas.atlas(atlas_xml,atlas_file,views=views)
    atlases[dim] = atlas
  return atlases

# Get pair of images, only available are currently 2 and 8 mm.
def get_pair_images(voxdims=["2","2"]):
  mr_directory = get_data_directory()
  image1 = "%s/%smm16_zstat1_1.nii" %(mr_directory,voxdims[0])
  image2 = "%s/%smm16_zstat3_1.nii" %(mr_directory,voxdims[1])
  return [image1,image2]
