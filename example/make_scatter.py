# Create a scatterplot from two brain images
from pybraincompare.mr.datasets import get_pair_images, get_mni_atlas
from pybraincompare.compare.mrutils import resample_images_ref, get_standard_brain, get_standard_mask, do_mask
from pybraincompare.compare.maths import calculate_correlation
from pybraincompare.compare import scatterplot, atlas as Atlas
from pybraincompare.template.visual import view
from nilearn.image import resample_img
import numpy
import nibabel

# SCATTERPLOT COMPARE ---- (with nifti input) ---------------------------------------------------

# Images that we want to compare - they must be in MNI space
image_names = ["image 1","image 2"]
images = get_pair_images(voxdims=["2","8"])

html_snippet,data_table = scatterplot.scatterplot_compare(images=images,
                                                     image_names=image_names,
                                                     corr_type="pearson") 
view(html_snippet)

# RESAMPLING IMAGES -----------------------------------------------------------------------------

# If you use your own standard brain (arg reference) we recommend resampling to 8mm voxel
# Here you will get the resampled images and mask returned
reference = nibabel.load(get_standard_brain("FSL"))
images_resamp,ref_resamp = resample_images_ref(images,
                                               reference=reference,
                                               interpolation="continuous",
                                               resample_dim=[8,8,8])

# SCATTERPLOT COMPARE ---- (with vector input) ---------------------------------------------------

# We are also required to provide atlas labels, colors, and correlations, so we calculate those in advance
# pybraincompare comes with mni atlas at 2 resolutions, 2mm and 8mm
# 8mm is best resolution for rendering data in browser, 2mm is ideal for svg renderings
atlases = get_mni_atlas(voxdims=["8","2"])
atlas = atlases["8"]
atlas_rendering = atlases["2"] 

# This function will return a data frame with image vectors, colors, labels
# The images must already be registered / in same space as reference
corrs_df = calculate_correlation(images=images_resamp,mask=ref_resamp,atlas=atlas,corr_type="pearson")

html_snippet,data_table = scatterplot.scatterplot_compare_vector(image_vector1=corrs_df.INPUT_DATA_ONE,
                                                                 image_vector2=corrs_df.INPUT_DATA_TWO,
                                                                 image_names=image_names,
                                                                 atlas=atlas_rendering,
                                                                 atlas_vector = corrs_df.ATLAS_DATA,
                                                                 atlas_labels=corrs_df.ATLAS_LABELS,
                                                                 atlas_colors=corrs_df.ATLAS_COLORS,
                                                                 corr_type="pearson")
view(html_snippet)


# CUSTOM ATLAS ---------------------------------------------------------------------------------

# You can specify a custom atlas, including a nifti file and xml file
# atlas = Atlas.atlas(atlas_xml="MNI.xml",atlas_file="MNI.nii") 
# Default slice views are "coronal","axial","sagittal"
