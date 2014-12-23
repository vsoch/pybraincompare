# Create a scatterplot from two brain images
from compare import compare

# Images that we want to compare
image1 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/2mm16_zstat1_1.nii"
image2 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/2mm16_zstat3_1.nii"

# A table file path (that does or does not exist) for the data
voxel_resample = [8,8,8]
html_snippet = compare.scatterplot_compare(image1=image1,image2=image2,software="FREESURFER",voxdim=voxel_resample)

