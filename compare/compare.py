import nibabel
from mrutils import get_standard_mask, do_mask
from templates import get_template, add_string
from futils import get_name
import pandas
import numpy
import os
import atlas

# Unbiased visual comparison with scatterplot
"Generate a d3 scatterplot for two registered, standardized images."
def scatterplot_compare(image1,image2,software="FSL",voxdim=[8,8,8],atlas=None,corr=None):

  # Get the reference brain mask
  reference = get_standard_mask(software)
  masked = do_mask(images=[image1,image2],mask=reference,resample_dim=voxdim)
  masked = pandas.DataFrame(numpy.transpose(masked))

  if atlas:
    masked_atlas = do_mask(images = atlas.file,mask=reference,resample_dim=voxdim,interpolation="nearest")
    masked["ATLAS_DATA"] = numpy.transpose(masked_atlas)
    # Prepare label (names)
    labels = ['"%s"' %(atlas.labels[str(int(x))].label) for x in masked_atlas[0]]
    masked["ATLAS_LABELS"] = labels
    # Prepare colors - value of 0 == no label or just empty space, they are equivalent
    colors = ['"%s"' %(atlas.color_lookup[x.replace('"',"")]) for x in labels]
    masked["ATLAS_COLORS"] = colors
    # The column names MUST correspond to the replacement text in the file
    masked.columns = ["INPUT_DATA_ONE","INPUT_DATA_TWO","ATLAS_DATA","ATLAS_LABELS","ATLAS_COLORS"]
    # Get template
    template = get_template("scatter_atlas",masked)
    # Add SVGs - key value of svgs == text substitution in template, eg atlas_key["coronal"] replaces [coronal]
    template = add_string(atlas.svg,template)
    # ADD HERE - if user wants to do pearson correlation
    if corr:
      print "We will do pearson correlation!"
    # Finally, add image names
    template = add_string({"image 1":get_name(image1),"image 2":get_name(image2)},template)
  else:
    masked.columns = ["INPUT_DATA_ONE","INPUT_DATA_TWO"]
    template = get_template("scatter",masked)
  
  # Return complete html and raw data
  return template,masked
