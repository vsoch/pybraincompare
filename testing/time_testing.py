import time
import nibabel
from testing_functions import run_scatterplot_compare, get_images, get_atlas
from compare.mrutils import resample_images_ref
from compare import atlas as Atlas

# The ability to specify a voxel dimension has been removed, so this test code is for documentation only
voxdims = [[2,2,2],[3,3,3],[4,4,4],[5,5,5],[6,6,6],[8,8,8],[9,9,9]]
total_times = []
images = get_images()
atlas = get_atlas()

# Here we will run scatterplot compare WITH resampling images
for voxdim in voxdims:
  start_time = time.time()
  run_scatterplot_compare(images=images,image_names=["image 1","image 2"],voxdim=voxdim,atlas=atlas)
  end_time = time.time() - start_time
  print("--- %s seconds ---" % (end_time))
  total_times.append(end_time)

# without atlas resampling
# --- 2.77834582329 seconds ---
# --- 2.78794503212 seconds ---
# --- 2.84847187996 seconds ---
# --- 2.86263585091 seconds ---
# --- 2.85201501846 seconds ---
# --- 2.79989600182 seconds ---
# --- 2.7787270546 seconds ---

# with atlas resampling
# --- 9.41706585884 seconds ---
# --- 9.44414401054 seconds ---
# --- 9.363904953 seconds ---
# --- 9.30472588539 seconds ---
# --- 9.29344415665 seconds ---
# --- 9.31614303589 seconds ---

# Now no resampling for anyone! These images were resampled / registered in advance, the idea
# being we would save a transformation for comparison in NeuroVault
image1 = "../mr/8mm16_zstat1_1.nii"
image2 = "../mr/8mm16_zstat3_1.nii"
atlas_file = "../mr/MNI-maxprob-thr25-8mm.nii"
atlas_xml = "../mr/MNI.xml"
atlas_render = "../mr/MNI-maxprob-thr25-2mm.nii"
# Our standard also needs to have the same shape and affine, so resampling is not done
standard = "../mr/MNI152_T1_8mm_brain_mask.nii.gz"
atlas = Atlas.atlas(atlas_xml,atlas_file)
atlas_rendering = Atlas.atlas(atlas_xml,atlas_render)
images = [image1,image2]

# Now we can run the scatterplot compare, and test with and without atlas
start_time = time.time()
run_scatterplot_compare(images=images,image_names=["image 1","image 2"],
                        reference_mask=standard,atlas=None)
end_time = time.time() - start_time
print("--- %s seconds ---" % (end_time))

# without atlas
# --- 0.973186016083 seconds ---

start_time = time.time()
run_scatterplot_compare(images=images,image_names=["image 1","image 2"],
                        reference_mask=standard,atlas=atlas,atlas_rendering=atlas_rendering)
end_time = time.time() - start_time
print("--- %s seconds ---" % (end_time))

# with atlas
# --- 0.383077859879 seconds ---
# woot!
