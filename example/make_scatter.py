# Create a scatterplot from two brain images
from compare import compare, atlas as Atlas

# Images that we want to compare
image1 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/2mm16_zstat1_1.nii"
image2 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/2mm16_zstat3_1.nii"

# A table file path (that does or does not exist) for the data
voxel_resample = [8,8,8]
html_snippet,data_table = compare.scatterplot_compare(image1=image1,image2=image2,software="FREESURFER",voxdim=voxel_resample)

# Color based on atlas labels
atlas_file = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI-maxprob-thr25-2mm.nii"
atlas_xml = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI.xml"
mni_atlas = Atlas.atlas(atlas_xml,atlas_file)

html_snippet,data_table = compare.scatterplot_compare(image1=image1,image2=image2,software="FREESURFER",voxdim=voxel_resample,atlas=mni_atlas)


