import nibabel
from mrutils import get_standard_mask, do_mask
from templates import get_template
import pandas
import numpy
import os

# Unbiased visual comparison with scatterplot
"Generate a d3 scatterplot for two registered, standardized images."
def scatterplot_compare(image1,image2,software="FSL",voxdim=[8,8,8]):

  # Get the reference brain mask
  reference = get_standard_mask(software)
  masked = do_mask(images=[image1,image2],mask=reference,resample_dim=voxdim)
  masked = pandas.DataFrame(numpy.transpose(masked))
  # The column names MUST correspond to the replacement text in the file
  masked.columns = ["INPUT_DATA_ONE","INPUT_DATA_TWO"]

  # Get template with data path
  template = get_template("scatter",masked)
  
  # Return complete html!
  return template
  

