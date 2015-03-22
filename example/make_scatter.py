# Create a scatterplot from two brain images
from pybraincompare.mr.datasets import get_pair_images, get_mni_atlas
from pybraincompare.compare.mrutils import resample_images_ref, get_standard_brain
from pybraincompare.compare import compare, atlas as Atlas
from pybraincompare.template.visual import view
from nilearn.image import resample_img
import numpy
import nibabel

# SCATTERPLOT COMPARE ---------------------------------------------------------------------------------

# Images that we want to compare - they must be in MNI space
image_names = ["image 1","image 2"]
images = get_pair_images(voxdims=["2","8"])

html_snippet,data_table = compare.scatterplot_compare(images=images,
                                                     image_names=image_names,
                                                     corr_type="pearson") 
view(html_snippet)

# CUSTOM ATLAS ---------------------------------------------------------------------------------

# You can specify a custom atlas, including a nifti file and xml file
# atlas = Atlas.atlas(atlas_xml="MNI.xml",atlas_file="MNI.nii") 
# Default slice views are "coronal","axial","sagittal"
atlas = get_mni_atlas(voxdims=["8"])
atlas = atlas["8"] 

# RESAMPLING IMAGES ---------------------------------------------------------------------------------

# If you use your own standard brain (arg reference) we recommend resampling to 8mm voxel
# Here you will get the resampled images and mask returned
reference = nibabel.load(get_standard_brain("FSL"))
images_resamp,ref_resamp = resample_images_ref(images,
                                               reference=reference,
                                               interpolation="continuous",
                                               resample_dim=[8,8,8])
