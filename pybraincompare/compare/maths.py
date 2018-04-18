'''
maths.py: part of pybraincompare package
Simple math functions

'''
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from builtins import str
from builtins import range
from past.utils import old_div
from .mrutils import (
    apply_threshold,
    do_mask,
    generate_thresholds,
    resample_images_ref
)
from scipy.stats import pearsonr, spearmanr, norm, t
import numpy as np
from . import maths
import pandas
import nibabel
import sys
import os


def percent_to_float(x):
    return old_div(float(x.strip('%')),100)

def calculate_correlation(images,
                          mask=None,
                          atlas=None,
                          summary=False, 
                          corr_type="pearson"):

    '''calculate_correlation
    Calculate a correlation between two images
    
    images: list nibabel.Nifti1Image objects
        list of 2 nibabel objects

    corr_type: str
        correlation type pearson or spearman [default pearson]

    atlas: pybraincompare.compare.atlas
        a pybraincompare atlas object [optional]

    Calls calculate_pairwise_correlation, or calculate_atlas_correlation,
    which work with vectors. If you do masking of images an atlas on your
    own, you can call these other functions directly to produce a single
    or regional correlation.

    If an atlas is supplied, will return a data frame as follows:
    
    summary: boolean
        If True, return only the regional labels with correlations
        If False, return entire dataframe 
    '''
    if mask != None:
        masked = do_mask(images=images,mask=mask)

    # No mask means we include all voxels, including outside brain
    else:
        masked =  np.vstack((np.array(images[0].get_data().flatten()),
                             np.array(images[1].get_data().flatten())))

    # A return value of "nan" indicates that there was not overlap
    if np.isnan(masked).all():
        corr = np.nan

    else:
        # If we want a whole brain correlation score, (no atlas specified)
        if atlas == None:
            corr = calculate_pairwise_correlation(masked[0],
                                                  masked[1],
                                                  corr_type=corr_type)

        else:  
            atlas_nii = nibabel.load(atlas.file)

            if not (atlas_nii.get_affine() == images[0].get_affine()).all():  
                atlas_nii, _ = resample_images_ref(images=atlas.file,
                                                   reference=images[0],
                                                   interpolation="nearest")

            atlas_vector = do_mask(atlas_nii,mask=mask)[0]
            atlas_labels =  ['"%s"' %(atlas.labels[str(int(x))].label) 
                             for x in atlas_vector]
            atlas_colors = ['"%s"' %(atlas.color_lookup[x.replace('"',"")]) 
                             for x in atlas_labels]

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

def calculate_pairwise_correlation(image_vector1,
                                   image_vector2,
                                   corr_type="pearson",
                                   atlas_vector=None):   

    '''calculate_pairwise_correlation
    Calculate a correlation value for two vectors
    
    image_vector1,image_vector2: vectors of equal length with image values
    
    corr_type: 
        correlation type [default pearson]
    
    atlas_vector: 
        single vector of region labels strings [optional]

    If an atlas_vector is supplied, returns dictionary with atlas labels
    If not, returns single correlation value
    '''

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
            corr,pval = pearsonr(image_vector1, image_vector2)
            correlations = corr
        elif corr_type == "spearman": 
            corr,pval = spearmanr(image_vector1, image_vector2)
            correlations = corr 
    return correlations

def calculate_atlas_correlation(image_vector1,
                                image_vector2,
                                atlas_vector,
                                atlas_labels,
                                atlas_colors,
                                corr_type="pearson",
                                summary=False):

    '''calculate_atlas_correlation
    Return regional correlations from an atlas object:

    image_vector1,image_vector2: 
        vectors of equal length with image values
    
    atlas_vector: 
        vector of atlas labels same length as image vector
    
    corr_type: str
        pearson or spearman
    
    summary: boolean
        If True, return only the regional labels with correlations
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
  

def do_multi_correlation(image_df,corr_type="pearson"):
    '''comparison for an entire pandas data frame'''
    return image_df.corr(method=corr_type, min_periods=1)


def calc_rows_columns(ratio, n_images):
    '''from chrisfilo https://github.com/chrisfilo/mriqc'''
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

def TtoZ(t_stat_map,output_nii,dof):
    '''TtoZ: 
    for details see
    https://github.com/vsoch/TtoZ
    Also provided for command line.

    t_stat_map: 
        file path to t stat image

    output_nii: 
        output nifti file
    
    dof: 
        degrees of freedom (typically number subjects - 2)

    '''
    print("Converting map %s to Z-Scores..." %(t_stat_map))
  
    mr = nibabel.load(t_stat_map)
    data = mr.get_data()

    # Select just the nonzero voxels
    nonzero = data[data!=0]

    # We will store our results here
    Z = np.zeros(len(nonzero))

    # Select values less than or == 0, and greater than zero
    c  = np.zeros(len(nonzero))
    k1 = (nonzero <= c)
    k2 = (nonzero > c)

    # Subset the data into two sets
    t1 = nonzero[k1]
    t2 = nonzero[k2]

    # Calculate p values for <=0
    p_values_t1 = t.cdf(t1, df = dof)
    z_values_t1 = norm.ppf(p_values_t1)

    # Calculate p values for > 0
    p_values_t2 = t.cdf(-t2, df = dof)
    z_values_t2 = -norm.ppf(p_values_t2)
    Z[k1] = z_values_t1
    Z[k2] = z_values_t2

    # Write new image to file
    empty_nii = np.zeros(mr.shape)
    empty_nii[mr.get_data()!=0] = Z
    Z_nii_fixed = nibabel.nifti1.Nifti1Image(empty_nii,
                                             affine=mr.get_affine(),
                                             header=mr.get_header())
    nibabel.save(Z_nii_fixed,output_nii)

# From Chrisfilo alleninf

def nifti_file(string):
    if not os.path.exists(string):
        msg = "%r does not exist" % string
        raise argparse.ArgumentTypeError(msg)
    try:
        nii = nibabel.load(string)
    except IOError as e:
        raise argparse.ArgumentTypeError(str(e))
    except:
        msg = "%r is not a nifti file" % string
        raise argparse.ArgumentTypeError(msg)
    else:
        if len(nii.shape) == 4 and nii.shape[3] > 1:
            msg = "%r is four dimensional" % string
            raise argparse.ArgumentTypeError(msg)
    return string
