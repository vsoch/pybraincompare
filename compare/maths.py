'''
maths.py: part of pybraincompare package
Simple math functions

'''

from scipy.stats import pearsonr, spearmanr
import numpy as np
import maths

def percent_to_float(x):
  return float(x.strip('%'))/100

'''Calculate a correlation value for two images, returns correlation
- image_vector1: single vector of image values
- image_vector2: single vector of image values
- corr_type: correlation type [default pearson]
- atlas_vector: single vector of region labels strings [optional]
'''
def do_pairwise_correlation(image_vector1,image_vector2,corr_type="pearson",atlas_vector=None):   
  correlations = dict()

  # If we have atlas labels, return vector with labels
  if atlas_vector is not None:
    labs = np.unique(atlas_vector)
    for l in labs:
      if corr_type == "spearman": 
        corr,pval = spearmanr(image_vector1[np.where(atlas_vector == l)[0]],
                              image_vector2[np.where(atlas_vector == l)[0]])
        correlations[str(l)] = corr
      elif corr_type == "pearson": 
        corr,pval = pearsonr(image_vector1[np.where(atlas_vector == l)[0]],
                              image_vector2[np.where(atlas_vector == l)[0]])        
        correlations[str(l)] = corr

  else:
    if corr_type == "pearson": 
      correlations["No Label"] = pearsonr(image_vector1,image_vector2)
    elif corr_type == "spearman": 
      correlations["No Label"] = spearmanr(image_vector1,image_vector2)
  return correlations


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
