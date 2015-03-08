# Create a scatterplot from two brain images
from compare.mrutils import resample_images_ref
from compare import compare, atlas as Atlas
from nilearn.image import resample_img
from template.visual import view
import numpy

# Images that we want to compare - they must be in the same space, size
image1 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/2mm16_zstat1_1.nii"
image2 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/2mm16_zstat3_1.nii"
images = [image1,image2]

# Here is how we would first resample to another size
images, ref_4mm = resample_images_ref(images,image1,interpolation="continuous",resample_dim=[8,8,8])

# We will color based on atlas labels - the atlas must also be in same space, size
atlas_file = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI-maxprob-thr25-2mm.nii"
atlas_xml = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI.xml"
atlas = Atlas.atlas(atlas_xml,atlas_file) # Default slice views are "coronal","axial","sagittal"

# Create d3 scatterplot with atlas - specify to include pearson correlation
html_snippet,data_table = compare.scatterplot_compare(images,software="FREESURFER",atlas=atlas,corr="pearson")
