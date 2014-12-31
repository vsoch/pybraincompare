import nibabel
from mrutils import get_standard_mask, do_mask
from templates import get_template
import pandas
import numpy
import os
import atlas

# Unbiased visual comparison with scatterplot
"Generate a d3 scatterplot for two registered, standardized images."
def scatterplot_compare(image1,image2,software="FSL",voxdim=[8,8,8],atlas=None):

  # Get the reference brain mask
  reference = get_standard_mask(software)
  masked = do_mask(images=[image1,image2],mask=reference,resample_dim=voxdim)
  masked = pandas.DataFrame(numpy.transpose(masked))

  if atlas:
    masked_atlas = do_mask(images = atlas.file,mask=reference,resample_dim=voxdim,interpolation="nearest")
    masked["ATLAS_DATA"] = numpy.transpose(masked_atlas)
    # Prepare label (names)
    labels = [atlas.labels[str(int(x))].label for x in masked_atlas[0]]
    masked["ATLAS_LABELS"] = labels
    # The column names MUST correspond to the replacement text in the file
    masked.columns = ["INPUT_DATA_ONE","INPUT_DATA_TWO","ATLAS_DATA","ATLAS_LABELS"]
    # ADD HERE - svg images for atlas
    template = get_template("scatter_atlas",masked)
  else:
    masked.columns = ["INPUT_DATA_ONE","INPUT_DATA_TWO"]
    template = get_template("scatter",masked)
  
  # Return complete html and raw data
  return template,masked
