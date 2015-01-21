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
# image_files can be vector of svg/png images to represent images in vis. Optional!

# Note: the above does not take a "query" interest into account - it returns all images
# The next version will sort based on similarity to one of the query images.
