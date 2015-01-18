# Create a scatterplot from two brain images
from compare import compare, atlas as Atlas
from template.visual import view

# Images that we want to compare
image1 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/2mm16_zstat1_1.nii"
image2 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/2mm16_zstat3_1.nii"

# Color based on atlas labels
voxel_resample = [8,8,8]
atlas_file = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI-maxprob-thr25-2mm.nii"
atlas_xml = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI.xml"
atlas = Atlas.atlas(atlas_xml,atlas_file,views=["coronal"]) # custom set of views
atlas = Atlas.atlas(atlas_xml,atlas_file) # Default slice views are "coronal","axial","sagittal"

# Create d3 scatterplot with atlas - specify to include pearson correlation
html_snippet,data_table = compare.scatterplot_compare(image1=image1,image2=image2,software="FREESURFER",voxdim=voxel_resample,atlas=atlas,corr="pearson")

# View in browser!
view(html_snippet)
