'''
inference.py: part of pybraincompare package
Functions to calculate reverse inference

'''
from __future__ import print_function
from __future__ import division

from builtins import range
from past.utils import old_div
from pybraincompare.ontology.graph import get_node_fields, get_node_by_name
from pybraincompare.compare.maths import calculate_pairwise_correlation
from pybraincompare.compare.mrutils import get_images_df
from glob import glob
import nibabel
import pickle
import pandas
import numpy
import math
import re
import os


def likelihood_groups_from_tree(tree,standard_mask,input_folder,image_pattern="[0]+%s[.]",
                                output_folder=None,node_pattern="[0-9]+",):
    '''likelihood_groups_from_tree
    Function to generate likelihood groups from a pybraincompare.ontology.tree 
    object. These groups can then be used to calculate likelihoods (eg, 
    p(activation|cognitive process). The groups are output as pickle objects. 
    This is done because it is ideal to calculate likelihoods on a cluster.

    :param tree: dict
        a dictionary of nodes, with base nodes matching a particular pattern 
        assumed to be image (.nii.gz) files.

    :param standard_mask: nifti image (nibabel) 
        standard image mask that images are registered to

    :param output_folder: path
        a folder path to save likelihood groups

    :param input_folder: path
        the folder of images to be matched to the nodes of the tree.

    :param pattern: str 
        the pattern to match to find the base image nodes. Default is a number 
        of any length [neurovault image primary keys].

    :param image_pattern: str
        a regular expression to find image files in images_folder. Default will 
        match any number of leading zeros, any number, and any extension.

    :param node_pattern: str
        a regular expression to find image nodes in the tree, matched to name

    :return groups: pickle 
        a pickle with the following

    ..note::

            pbc_likelihood_groups_trm_12345.pkl
            
            group["nid"] = "trm_12345"
            group["in"] = ["path1","path2",..."pathN"]
            group["out"] = ["path3","path4",..."pathM"]
            group["meta"]: meta data for the node
            group["range_table"]: a data frame of ranges with "start" and "stop"
                      to calculate the range is based on the mins and max of 
                      the entire set of images

    '''
    # Find all nodes in the tree, match to images in folder
    nodes = get_node_fields(tree,field="name",nodes=[])
    contender_files = glob("%s/*" %input_folder)

    # Images will match the specified pattern
    find_nodes = re.compile(node_pattern)
    image_nodes = [node for node in nodes if find_nodes.match(node)]
    image_nodes = numpy.unique(image_nodes).tolist()

    # Node names must now be matched to files
    file_lookup = dict()
    file_names = [os.path.split(path)[-1] for path in contender_files]
    for node in image_nodes:
        find_file = re.compile(image_pattern %node)
        idx = [file_names.index(x) for x in file_names if find_file.match(x)]
        if len(idx) > 1:
            raise ValueError("ERROR: found %s images that match pattern %s." %len(idx),find_file.pattern)
        elif len(idx) == 0:
            print("Did not find file for %s, will not be included in analysis." %(node))
        else:
            file_lookup[node] = contender_files[idx[0]]

    # Use pandas dataframe to not risk weird dictionary iteration orders
    files = pandas.DataFrame(list(file_lookup.values()),columns=["path"])
    files.index = list(file_lookup.keys())
 
    # The remaining nodes in the tree (that are not images) will have a RI score
    concept_nodes = [x for x in nodes if x not in image_nodes] 

    # create table of voxels for all images (the top node)
    mr = get_images_df(file_paths=files.path,mask=standard_mask)
    mr.index = files.index

    range_table = make_range_table(mr)

    # GROUPS ----------------------------------------------------
    # Find groups for image sets at each node (**node names must be unique) 
    # This is images at (and in lower levels) of node vs. everything else
    # will be used to calculate p([activation in range | region (voxel)]

    groups = []

    for concept_node in concept_nodes:
        node = get_node_by_name(tree,concept_node)
        node_id = node["nid"] # for save image
        node_meta = node["meta"]
        if node:
            all_children = get_node_fields(node,"name",[])
            children_in = [c for c in all_children if c in files.index]
            children_out = [c for c in files.index if c not in children_in]
            if len(children_in) > 0 and len(children_out) > 0:
                print("Generating group for concept node %s" %(concept_node))
                group = {"in": files.path.loc[children_in].unique().tolist(),
                         "out": files.path.loc[children_out].unique().tolist(),
                         "range_table": range_table,
                         "meta": node_meta,
                         "nid": node_id,
                         "name": concept_node}                

                groups.append(group)
                if output_folder != None:
                    outpkl = "%s/pbc_group_%s.pkl" %(output_folder,node_id)
                    pickle.dump(group, open(outpkl,"wb"))

    return groups

def make_range_table(mr,ranges=None):
    '''make_range_table
    Generate a table of ranges, in format

    ..note::

                       start  stop
        [-28.0,-27.5]  -28.0 -27.5
        [-27.5,-27.0]  -27.5 -27.0
        [-27.0,-26.5]  -27.0 -26.5
        [-26.5,-26.0]  -26.5 -26.0

        from a table of values, where images/objects are expected in rows, 
        and regions/voxels in columns

        ranges, if defined, should be a list of lists of ranges to
        extract. eg, [[start,stop],[start,stop]] where start is min, stop is max

        The absolute min and max are used to generate a table of ranges
        in the format above from min to max

    '''

    range_table = pandas.DataFrame(columns=["start","stop"])

    if ranges:
        error = "ERROR: ranges should be a list of ranges [[start,stop], ...]"
        if not isinstance(ranges,list):
            raise ValueError(error)    
        for range_group in ranges:
           if not isinstance(range_group,list) or len(range_group) != 2:
               raise ValueError(error)    
           name = "[%s,%s]" %(range_group[0],range_group[1])
           range_table.loc[name] = [range_group[0],range_group[1]]           

    # If no start or stop defined, get from min and max of data
    else:    
        mins = mr.min(axis=0)
        maxs = mr.max(axis=0)
        absmin = math.floor(numpy.min(mins))
        absmax = math.ceil(numpy.max(maxs))
        steps = ((abs(absmin)+absmax)*2)+1
        breaks = numpy.linspace(absmin,absmax,num=steps,retstep=True)[0]
        for s in range(0,len(breaks)-1):
            start = breaks[s]
            stop = breaks[s+1]
            name = "[%s,%s]" %(start,stop)
            range_table.loc[name] = [start,stop]
    
    return range_table


def get_likelihood_df(nid,in_images,out_images,standard_mask,range_table,
                      threshold=2.96,output_folder=None,method=["binary"]):

    '''get_likelihood_df

    will calculate likelihoods and save to a pandas df pickle. 
    The user must specify the method [default is binary]. 
    Method details:

    ranges:
        - likelihood in all thresholds defined (calculate_priors in ranges)
    binary
        - likelihood above / below a certain level [threshold, default=2.96]

    Note: you do not need to calculate likelihoods in advance for the mean metric
    (using a derivation of the distance from a mean image as a probability score)
    In this case, use calculate_reverse_inference_distance
 
    :param nid: str
        a unique identifier, a node ID from pybraincompare.ontology.tree

    :param in_images: list
        a list of files for the "in" group relevant to some concept

    :param out_images: list
        the rest

    :param standard_mask: nibabel.Nifti1Image object
        the standard mask images are in space of

    :param range_table: pandas data frame
        a data frame of ranges with "start" and "stop" to calculate
        the range is based on the mins and max of the entire set of images
        can be generated with pybraincompare.inference.make_range_table

    :param output_folder: path
        folder to save likelihood pickles [default is None]

  
    If output_folder is not specified, the df objects are returned.
    If specified, will return paths to saved pickle objects:
    pbc_likelihood_trm12345_df_in.pkl

    EACH VOXEL IS p(activation in voxel is in threshold)

    '''
    # Read all images into one data frame
    if len(numpy.intersect1d(in_images,out_images)) > 0:
        raise ValueError("ERROR: in_images and out_images should not share images!")
    all_images = in_images + out_images
    mr = get_images_df(file_paths=all_images,mask=standard_mask)
    mr.index = all_images
    in_subset = mr.loc[in_images]
    out_subset = mr.loc[out_images] 

    # Calculate likelihood for user defined methods
    df = dict()    
    if "ranges" in method:
        df["out_ranges"] = calculate_likelihood_in_ranges(in_subset,range_table)
        df["in_ranges"] = calculate_likelihood_in_ranges(out_subset,range_table)
        if output_folder:
            df["in_ranges"] = save_likelihood_pickle(df["in_ranges"],
                                                     output_folder,nid,"in_ranges")         

            df["out_ranges"] = save_likelihood_pickle(df["out_ranges"],
                                                      output_folder,nid,"out_ranges")         

    if "binary" in method:
        df["in_bin"] = calculate_likelihood_binary(in_subset,threshold)
        df["out_bin"] = calculate_likelihood_binary(out_subset,threshold)
        if output_folder:
            df["in_bin"] = save_likelihood_pickle(df["in_bin"],
                                                  output_folder,
                                                  nid, "in_bin_%s" %threshold)         

            df["in_out"] = save_likelihood_pickle(df["out_bin"],
                                                  output_folder,
                                                  nid, "out_bin_%s" %threshold)         
     
    return df 



def save_likelihood_pickle(likelihood_df,output_folder,nid,suffix):
    outfile = "%s/pbc_likelihood_%s_df_%s.pkl" %(output_folder,nid,suffix)
    likelihood_df.to_pickle(outfile)
    return outfile


def save_likelihood_nii(input_pkl,output_folder,standard_mask):
    '''save_likelihood_nii

    save a nii image for each threshold (column) across all voxels (rows)

    :param input_pkl: pickle object
        the input pickle with likelihood saved by
                  pybraincompare.ontology.inference.get_likelihood_df

    :param output_folder: path
        folder for output nifti, one per threshold range

   
    pbc_likelihood_trm12345_df_in_[start]_[stop].nii
    EACH VOXEL IS p(activation in voxel is in threshold) for group [in or out]

    '''

    likelihood = pandas.read_pickle(input_pkl)
    ranges = likelihood.columns.tolist()
    standard_brain = nibabel.load(standard_mask)

    for range_group in ranges:
        empty_nii = numpy.zeros(shape=standard_brain.shape)
        try:
            range_group_str = range_group.replace(",","_to_").replace("[","").replace("]","")
        except:
            range_group_str = range_group
        probs = likelihood[range_group]
        empty_nii[standard_brain.get_data()!=0] = probs
        out_nii = nibabel.Nifti1Image(empty_nii,
                                      affine=standard_brain.get_affine())
        ofile = "%s/pbc_likelihood_%s_df.nii.gz" %(output_folder,
                                                  range_group_str)
        nibabel.save(out_nii, ofile)


def calculate_likelihood_in_ranges(region_df,ranges_df):
    '''calculate_likelihood_in_ranges 
    Function to calculate likelihood from a regionally-based df for ranges of values

    :param region_df: pandas data frame 
        a pandas data frame with voxels/regions in columns, images in rows
    :param range_df: pandas data frame
        a pandas data frame with columns ["start","stop"], 
        and each row corresponding to a particular range of values
    '''

    # A table of likelihood, columns --> thresholds, rows --> regions)
    likelihood = pandas.DataFrame(columns=ranges_df.index)  
    for row in ranges_df.iterrows(): 
        # Nan means that value does not pass
        bin_df = (region_df >= row[1].start) & (region_df <=row[1].stop)   
        # [Numerator] Count the number of True in each column 
        #    (meaning within range) add 1 for laplace smoothing
        # [Denominator] sum(numerator with no laplace) + 
        #     V (words in vocabulary --> regions/voxels)
        # [Overall] probability that the image voxel (region) is in 
        #    the range given entire image set
        numerator = bin_df.sum(axis=0)
        numerator_laplace_smoothed = numerator + 1
        denominator = numpy.sum(numerator) + bin_df.shape[1]
        likelihood[row[0]] = old_div(numerator_laplace_smoothed, denominator)
    return likelihood

def calculate_likelihood_binary(region_df,threshold=2.96):
    '''calculate_likelihood_binary
    Function to calculate likelihood for activation above/below some single threshold

    :param region_df: pandas data frame
        a pandas data frame with voxels/regions in columns, images in rows

    :param threshold: float
        a value that will be used to generate binary matrix (default is Z=2.96)

    '''

    bool_df = region_df.abs()
    bin_df = bool_df>=threshold
    # [Numerator] Count the non-NaN values in each column,
    #     add 1 for laplace smoothing
    # [Denominator] sum(numerator with no laplace) + 
    #     V (words in vocabulary --> regions/voxels)
    # [Overall] probability that the image voxel (region) 
    #    is in the range given entire image set
    numerator = bin_df.sum(axis=0)
    numerator_laplace_smoothed = numerator + 1
    denominator = numpy.sum(numerator) + bool_df.shape[1]
    result = pandas.DataFrame(old_div(numerator_laplace_smoothed, denominator))
    result.columns = [threshold] # store threshold with data frame
    return result

def calculate_reverse_inference_distance(query_image,
                                         in_images,
                                         out_images,
                                         standard_mask,
                                         equal_priors=True):    

    '''calculate_reverse_inference_distance

    return reverse inference value based on generating likelihood scores using distance
    of the query image from the group

    ..note::
        
        Reverse Inference Calculation ------------------------------------------------------------------
        P(node mental process|activation) = P(activation|mental process) * P(mental process)
        divided by
        P(activation|mental process) * P(mental process) + P(A|~mental process) * P(~mental process)
        P(activation|mental process): my voxelwise prior map

    :param query_image: nifti image path
        image that we want to calculate reverse inference score for

    :param subset_in: list of nifti files
        brain maps that are defined for the concept

    :param subset_out: list of nifti files
        the rest

    :param equal_priors: boolean
        use 0.5 as a prior for each group [default True]. If set to False, the
        frequency of the concept in the total set will be used. "True" is recommended for small sets.

    '''
    if len(numpy.intersect1d(in_images,out_images)) > 0:
        raise ValueError("ERROR: in_images and out_images should not overlap!")
    all_images = in_images + out_images
    mr = get_images_df(file_paths=all_images,mask=standard_mask)
    mr.index = all_images
    in_subset = mr.loc[in_images]
    out_subset = mr.loc[out_images] 
    if equal_priors:
        p_process_in = 0.5
        p_process_out = 0.5
    else:
        in_count = len(in_images)
        out_count = len(out_images) 
        total = in_count + out_count                      # total images
        p_process_in = old_div(float(in_count), total)    # % niftis in
        p_process_out = old_div(float(out_count), total)  # % out

    # Read in the query image
    query = get_images_df(file_paths=query_image,mask=standard_mask)

    # Generate a mean image for each group
    mean_image_in = pandas.DataFrame(in_subset.mean())
    mean_image_out = pandas.DataFrame(out_subset.mean())

    # p in/out is similarity between query image and groups
    p_in = numpy.power(calculate_pairwise_correlation(mean_image_in[0],
                                                      query[0]),2)
    p_out = numpy.power(calculate_pairwise_correlation(mean_image_out[0],
                                                      query[0]),2)

    # Calculate inference
    numerators = p_in * p_process_in
    denominators = (p_in * p_process_in) + (p_out * p_process_out)
    return (old_div(numerators, denominators))


def calculate_reverse_inference_threshes(p_in, p_out, 
                                         in_count, out_count,
                                         equal_priors=True):

    '''calculate_reverse_inferences_threshes

    return reverse inference value based on a likelihood matrix 
                   (no stat map as a query image)

    # Reverse Inference Calculation -------------------------------------------
    # P(node mental process|activation) = P(activation|mental process) * P(mental process)
    # divided by
    # P(activation|mental process) * P(mental process) + P(A|~mental process) * P(~mental process)
    # P(activation|mental process): my voxelwise prior map

    :param p_in: pandas data frame
        likelihood in table, columns are thresholds, rows are voxels
    :param p_out: pandas data frame
        likelihood out table, ""  ""
    :param in_count: int
        number of brain images used to generate p_in table
    :param out_count: int
        number of brain images used to generate p_out table

    '''
    total = in_count + out_count # total number of nifti images
    if equal_priors:
        p_process_in = 0.5
        p_process_out = 0.5
    else:
        p_process_in = old_div(float(in_count), total)   # % niftis in
        p_process_out = old_div(float(out_count), total) # % out    

    # If we multiply, we will get 0, so we take sum of logs
    p_in_log = numpy.log(p_in)
    p_out_log = numpy.log(p_out)
    numerators = p_in_log.sum(axis=0) * p_process_in
    denominators = (p_in_log.sum(axis=0) * p_process_in) + (p_out_log.sum(axis=0) * p_process_out)
    return (old_div(numerators, denominators))


def calculate_reverse_inference(mrtable, p_in, p_out,
                                in_count, out_count,
                                range_table=None,
                                equal_priors=True):

    '''calculate_reverse_inference
    Function to return reverse inference value based on particular thresholds 
    of a brain stat map (or average of the node set). This will return one 
    value! If a range table is provided, a reverse inference value is returned
    for each range defined in the table. If not, the likelihood table are 
    assumed to be done for a binary value, and this value (stored in the 
    column name of the likelihood table) is used to threshold the image, 
    and return a score based on that threshold.

    :param mrtable: pandas data frame
        should be a table, with the query image(s) in rows, and voxels/regions
        in columns if there is more than one image, a mean will be used

    :param p_in: pandas data frame
        the likelihood table for images that are relevant to the concept

    :param p_out: pandas data frame
        the likelihood table for images not relevant to the concept

    :param in_count: int
        the number of images used to generate the likelihood in table

    :param out_count: int
        the number of images used to generate the likelihood out table

    :param range_table: will be used to define ranges of interest. The image 
        will be thresholded for these ranges. if not provided, 
        image will be thresholded using threshold defined as
        column name in likelihood tables
    '''
    if not isinstance(mrtable,pandas.core.frame.DataFrame):
        mrtable = pandas.DataFrame(mrtable)
    # If we are given a DataFrame with multiple rows, take mean
    total = in_count + out_count # total number of nifti images
    if equal_priors:
        p_process_in = 0.5
        p_process_out = 0.5
    else:
        p_process_in = old_div(float(in_count), total)   # % niftis in
        p_process_out = old_div(float(out_count), total) # % out

    # If we multiply, we will get 0, so we take sum of logs
    if mrtable.shape[1]>1:
        mrtable = pandas.DataFrame(mrtable.mean())
    if isinstance(range_table,pandas.core.frame.DataFrame):
        p_in_vector,p_out_vector = _calculate_reverse_inference_vectors_ranges(mrtable,p_in,p_out,
                                                                   in_count,out_count,range_table)
    else:
        p_in_vector,p_out_vector = _calculate_reverse_inference_vectors_binary(mrtable,p_in,p_out,
                                                                               in_count,out_count)
    # Convert to logs
    p_in_log = numpy.log(p_in_vector)
    p_out_log = numpy.log(p_out_vector)
    if len(p_in_log)==0:
        numerator = 0.0
    else:
        numerator = p_in_log.sum(axis=0) * p_process_in
    if len(p_out_log)==0 and len(p_in_log)==0:
        denominator = 0.0 
    elif len(p_in_log)==0:
        denominator = (p_out_log.sum(axis=0) * p_process_out)
    else:       
        denominator = (p_in_log.sum(axis=0) * p_process_in) + (p_out_log.sum(axis=0) * p_process_out)
    if numerator == 0.0 and denominator == 0.0:
        return 0.0
    else: 
        return (old_div(numerator, denominator))

def _calculate_reverse_inference_vectors_ranges(mrtable,
                                                p_in,p_out,
                                                in_count,out_count,
                                                range_table):
    '''
    Internal function to return two strings of probabilities: 
    one for probabilities from likelihood table for voxels with activations
    [p_in_vector], and the other to return probabilities for voxels without 
    activation [p_out_vector]. These probabilities can go into a reverse 
    inference calculation for calculating a score based on binarizing an image. 
    '''

    # For each ACTUAL voxel value, assign to its threshold
    stat_map_levels = pandas.DataFrame(columns=mrtable.columns,index=mrtable.index)
    for row in range_table.iterrows():
        stat_map_levels[(mrtable >= row[1].start) & (mrtable <=row[1].stop)] = row[0]

    # use actual threshold labels to choose the appropriate probability values 
    # for each voxel
    p_in_vector = []  # a vector of probability values, using p_in as a lookup
    p_out_vector = []

    # For each threshold
    for v in range(0,stat_map_levels.shape[0]):
        level = stat_map_levels[0][v]

        # Look up the levels, append to our lists
        p_in_vector.append(p_in.loc[v,level])
        p_out_vector.append(p_out.loc[v,level])

    return p_in_vector,p_out_vector

def _calculate_reverse_inference_vectors_binary(mrtable, p_in, p_out,
                                                in_count,out_count):
    '''Internal function to return two strings of probabilities: one for 
       probabilities from likelihood table derived from images relevant to a 
       contrast, and the other from a likelihood table from images not relevant 
       - both are limited to voxels with activation for the image, defined as 
       above/below the threshold defined in the columns of the likelihood table.
       This will be use for reverse inference calculation of a single image 
       based on an absolute threshold to define activation. 
    '''
    # What voxels is the image > < the threshold?
    stat_map_abs = mrtable.abs()
    # Threshold should be equivalent in both p_in and p_out
    if p_in.columns[0] != p_out.columns[0]:
        raise ValueError("ERROR: threshold defined in likelihood 'in' and likelihood 'out' tables is different (%s vs %s)" %(p_in.columns[0],p_out.columns[0]))
    else:
        threshold = p_out.columns[0]
    bin_df = stat_map_abs[0] >= threshold
    p_in_vector = p_in[bin_df==True][threshold].tolist()
    p_out_vector = p_out[bin_df==True][threshold].tolist()
    return p_in_vector,p_out_vector
