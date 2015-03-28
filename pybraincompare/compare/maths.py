'''
maths.py: part of pybraincompare package
Simple math functions

'''

from mrutils import resample_images_ref, apply_threshold, generate_thresholds, do_mask
from scipy.stats import pearsonr, spearmanr
import numpy as np
import maths
import pandas
import nibabel

def percent_to_float(x):
  return float(x.strip('%'))/100

'''Calculate a correlation between two images
- images: list of 2 nibabel objects
- corr_type: correlation type pearson or spearman [default pearson]
- atlas: a pybraincompare atlas object [optional]

Calls calculate_pairwise_correlation, or calculate_atlas_correlation,
which work with vectors. If you do masking of images an atlas on your
own, you can call these other functions directly to produce a single
or regional correlation.

If an atlas is supplied, will return a data frame as follows:
- summary: If True, return only the regional labels with correlations
           If False, return entire dataframe 
'''
def calculate_correlation(images,mask=None,atlas=None,summary=False,corr_type="pearson"):

  if mask != None:
    masked = do_mask(images=images,mask=mask)
  else: # No mask means we include all voxels, including outside brain
    masked =  np.vstack((np.array(images[0].get_data().flatten()),
                         np.array(images[1].get_data().flatten())))

  # A return value of "nan" indicates that there was not overlap between mask and images
  if np.isnan(masked).all():
    corr = np.nan
  else:
    # If we want a whole brain correlation score, (no atlas specified)
    if atlas == None:
      corr = calculate_pairwise_correlation(masked[0],masked[1],corr_type=corr_type)
    else:  
      atlas_nii = nibabel.load(atlas.file)
      if not (atlas_nii.get_affine() == images[0].get_affine()).all():  
        atlas_nii, ref_nii = resample_images_ref(images=atlas.file,reference=images[0],
                                             interpolation="nearest")

      atlas_vector = do_mask(atlas_nii,mask=mask)[0]
      atlas_labels =  ['"%s"' %(atlas.labels[str(int(x))].label) for x in atlas_vector]
      atlas_colors = ['"%s"' %(atlas.color_lookup[x.replace('"',"")]) for x in atlas_labels]

      # Need to check here if we have overlap!
      if not np.isnan(atlas_vector).all():
        corr = calculate_atlas_correlation(image_vector1=masked[0],
                                       image_vector2=masked[1],
                                       atlas_vector=atlas_vector,
                                       atlas_labels=atlas_labels,
                                       atlas_colors=atlas_colors,
                                       corr_type=corr_type,
                                       summary=summary)
      else:
        corr = np.nan
  return corr

'''Calculate a correlation value for two vectors
- image_vector1,image_vector2: vectors of equal length with image values
- corr_type: correlation type [default pearson]
- atlas_vector: single vector of region labels strings [optional]

If an atlas_vector is supplied, returns dictionary with atlas labels
If not, returns single correlation value
'''
def calculate_pairwise_correlation(image_vector1,image_vector2,corr_type="pearson",
                                   atlas_vector=None):   
  correlations = dict()

  # If we have atlas labels, return vector with labels
  if atlas_vector is not None:
    labs = np.unique(atlas_vector)
    for l in labs:
      if corr_type == "spearman": 
        corr,pval = spearmanr(image_vector1[np.where(atlas_vector == l)[0]],
                              image_vector2[np.where(atlas_vector == l)[0]])
        correlations[str(int(l))] = corr
      elif corr_type == "pearson": 
        corr,pval = pearsonr(image_vector1[np.where(atlas_vector == l)[0]],
                              image_vector2[np.where(atlas_vector == l)[0]])        
        correlations[str(int(l))] = corr

  else:
    if corr_type == "pearson": 
      corr,pval = pearsonr(image_vector1,image_vector2)
      correlations = corr
    elif corr_type == "spearman": 
      corr,pval = spearmanr(image_vector1,image_vector2)
      correlations = corr 
  return correlations

'''Return regional correlations from an atlas object:
- image_vector1,image_vector2: vectors of equal length with image values
- atlas_vector: vector of atlas labels same length as image vector
- corr_type: pearson or spearman
- summary: If True, return only the regional labels with correlations
         If False, return entire dataframe 

if summary == False (default):
INPUT_DATA_1, INPUT_DATA_2: the values in the images
ATLAS_DATA: the value (integer) in the atlas, used to match to name labels
ATLAS_LABELS: region names extracted from the atlas.xml
ATLAS_CORR: the regional correlation for some point in input data 1 or 2
ATLAS_COLOR: a hex value to render in the final d3

If summary == True
returns only region labels and corresponding correlations
'''
def calculate_atlas_correlation(image_vector1,image_vector2,atlas_vector,atlas_labels,
                                atlas_colors,corr_type="pearson",summary=False):

  df = pandas.DataFrame()
  df["INPUT_DATA_ONE"] = image_vector1
  df["INPUT_DATA_TWO"] = image_vector2
  df["ATLAS_DATA"] = atlas_vector  
  df["ATLAS_LABELS"] = atlas_labels   
  
  corrs = calculate_pairwise_correlation(image_vector1,image_vector2,
                                         atlas_vector=atlas_vector,
                                         corr_type=corr_type)
  df["ATLAS_CORR"] = [corrs[str(int(x))] for x in atlas_vector]
  df["ATLAS_COLORS"] = atlas_colors   
  
  if summary == False: 
    return df
  else:
    regional = df.copy()
    regional = regional.loc[:,regional.columns[3:5]]
    regional = regional.drop_duplicates()
    return regional
  

'''comparison for an entire pandas data frame'''
def do_multi_correlation(image_df,corr_type="pearson"):
  return image_df.corr(method=corr_type, min_periods=1)

'''from chrisfilo https://github.com/chrisfilo/mriqc'''
def calc_rows_columns(ratio, n_images):
    rows = 1
    for _ in range(100):
        columns = math.floor(ratio * rows)
        total = rows * columns
        if total > n_images:
            break

        columns = math.ceil(ratio * rows)
        total = rows * columns
        if total > n_images:
            break
        rows += 1
    return rows, columns
