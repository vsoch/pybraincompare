# Create a scatterplot from two brain images
from compare.mrutils import resample_images_ref
from compare import compare, atlas as Atlas
from nilearn.image import resample_img
from template.visual import view
import numpy

# SCATTERPLOT COMPARE ---------------------------------------------------------------------------------

# Images that we want to compare - they must be in MNI space
image1 = "mr/8mm16_zstat1_1.nii"
image2 = "mr/2mm16_zstat3_1.nii" 
image_names = ["image 1","image 2"]
images = [image1,image2]

html_snippet,data_table = compare.scatterplot_compare(images=images,
                                                     image_names=image_names,
                                                     corr="pearson") 
view(html_snippet)

# CUSTOM ATLAS ---------------------------------------------------------------------------------

# You can specify a custom atlas, including a nifti file and xml file. Give to compare.scatterplot_compare as atlas=atlas
atlas_file = "mr/MNI-maxprob-thr25-8mm.nii"
atlas_xml = "mr/MNI.xml"
atlas = Atlas.atlas(atlas_xml,atlas_file) # Default slice views are "coronal","axial","sagittal"


# RESAMPLING IMAGES ---------------------------------------------------------------------------------

# If you use your own standard brain (arg reference_mask) we recommend resampling to 8mm voxel
# Here is how you would resample your images if they are differently sized. Both should already be in MNI
#   -  You will get the resampled images and mask returned
images_resamp,ref_resamp = resample_images_ref(images_nii,
                                               reference_mask=standard,
                                               interpolation="continuous")
                                               resample_dim=[8,8,8])
