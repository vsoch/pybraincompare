import nibabel
from mrutils import get_standard_mask, do_mask
from templates import get_template
import pandas
import numpy
import os

# Unbiased visual comparison with scatterplot
"Generate a d3 scatterplot for two registered, standardized images."
def scatterplot_compare(image1,image2,table_file,software="FSL",voxdim=[8,8,8]):

  # Get the reference brain mask
  reference = get_standard_mask(software)
  
  if not os.path.isfile(table_file):
    masked = do_mask(images=[image1,image2],mask=reference,resample_dim=voxdim)
    masked = pandas.DataFrame(numpy.transpose(masked))
    masked.to_csv(table_file,index=False,float_format='%.3f')

  # Get template with data path
  template = get_template("scatter",table_file)
  
  # Return complete html!
  return template
  

