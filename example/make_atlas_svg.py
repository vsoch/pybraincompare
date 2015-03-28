from pybraincompare.compare import atlas as Atlas
from pybraincompare.mr.datasets import get_mni_atlas

# Color based on atlas labels
atlases = get_mni_atlas(voxdims=["2"])
atlas = atlases["2"]

# We return both paths and entire svg file
atlas.svg["coronal"] 
atlas.paths["coronal"]

# Save svg views to file
output_directory = "/home/vanessa/Desktop"
atlas.save_svg(output_directory) # default will save all views generated
atlas.save_svg(output_directory,views=["coronal"]) # specify a custom set
