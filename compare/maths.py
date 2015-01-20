from scipy.stats import pearsonr
import numpy as np

def percent_to_float(x):
  return float(x.strip('%'))/100

'''Calculate a correlation value for two images, returns correlation
- image_vector1: single vector of image values
- image_vector2: single vector of image values
- corr_type: correlation type [default pearson]
- atlas_vector: single vector of region labels strings [optional]
- currently only pearson is supported
'''
def do_pairwise_correlation(image_vector1,image_vector2,corr_type="pearson",atlas_vector=None):   
  correlations = dict()
  if atlas_vector is not None:
    labs = np.unique(atlas_vector)
    for l in labs:
      correlations[str(l)] = do_pearson(image_vector1[np.where(atlas_vector == l)[0]],image_vector2[np.where(atlas_vector == l)[0]])
  else:
    correlations["No Label"] = do_pearson(image_vector1,image_vector2)
  return correlations

'''Pearson correlation'''
def do_pearson(image_vector1,image_vector2):
  corr,pval = pearsonr(image_vector1,image_vector2)
  return corr

'''comparison for an entire pandas data frame'''
def do_multi_correlation(image_df,corr_type="pearson"):
  return image_df.corr(method=corr_type, min_periods=1)
