# Create a scatterplot from two brain images
from compare import compare, atlas as Atlas

# Color based on atlas labels
atlas_file = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI-maxprob-thr25-2mm.nii"
atlas_xml = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI.xml"
atlas = Atlas.atlas(atlas_xml,atlas_file,views=["coronal"]) # custom set of views
atlas = Atlas.atlas(atlas_xml,atlas_file) # Default slice views are "coronal","axial","sagittal"

# We return both paths and entire svg file
atlas.svg["coronal"] 
atlas.paths["coronal"]

# Save svg views to file
output_directory = "/home/vanessa/Desktop"
atlas.save_svg(output_directory) # default will save all views generated
atlas.save_svg(output_directory,views=["coronal"]) # specify a custom set
