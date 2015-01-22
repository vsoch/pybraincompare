# This will generate an interactive web interface to find similar images
#from compare import compare, atlas as Atlas
from template.visual import view
from compare.compare import similarity_search
from glob import glob

# Images that we want to compare
mrs = glob("/home/vanessa/Documents/Work/BRAINBEHAVIOR/mrs/Z/*.nii")

# Create a list of tags for each image
tags = [["Z","brain"],["Z","brain"],["Z"]]

# Generate search interface
similarity_search(mr_paths=mrs,tags=tags,image_paths=None)
# image_files can be vector of svg/png images to represent imagbes in vis. Optional!

# Note: the above does not take a "query" interest into account - it returns all images
# The next version will sort based on similarity to one of the query images.

# STOPPED HERE - vanessa - next time

# - figure out how to pre-compute similarity matrices AND images in neurovault
# - modify function to take in pre-computed matrix and image paths
# - modify function to take in ONE of those image paths as the image of interest
# - dynamically generate some kind of comparison image in the top right, should be done
# with d3 when I select an image below
# - create some initial search page to select an image
# - add it all to NeuroVault
