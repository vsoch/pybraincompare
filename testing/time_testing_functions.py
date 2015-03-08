import time
import nibabel
from testing_functions import run_scatterplot_compare, run_scatterplot_compare_resample
from compare.mrutils import resample_images_ref

voxdims = [[2,2,2],[3,3,3],[4,4,4],[5,5,5],[6,6,6],[8,8,8],[9,9,9]]
total_times = []

# Here we will run scatterplot compare with resampling images
for voxdim in voxdims:
  start_time = time.time()
  run_scatterplot_compare_resample(voxdim)
  end_time = time.time() - start_time
  print("--- %s seconds ---" % (end_time))
  total_times.append(end_time)

# --- 2.74351501465 seconds ---
# --- 3.90375995636 seconds ---
# --- 2.08854794502 seconds ---
# --- 1.48969292641 seconds ---
# --- 1.2076189518 seconds ---
# --- 0.957742929459 seconds ---
# --- 0.922529220581 seconds ---

# Now no resampling, and we will pretend these images are already generated
#image1 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/8mm16_zstat1_1.nii"
#image2 = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/8mm16_zstat3_1.nii"
#atlas_file = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI-maxprob-thr25-8mm.nii"
#atlas_xml = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/mr/MNI.xml"
#images = [image1,image2]

# Now we can run the scatterplot compare
#start_time = time.time()
#run_scatterplot_compare(images,atlas_file,atlas_xml)
#end_time = time.time() - start_time
#print("--- %s seconds ---" % (end_time))


