'''
inference.py: part of pybraincompare package
Functions to calculate reverse inference

'''

from pybraincompare.ontology.graph import get_node_fields, get_node_by_name
from pybraincompare.compare.mrutils import get_images_df
from glob import glob
import nibabel
import pickle
import pandas
import numpy
import math
import re
import os

'''
priors_groups_from_tree: Function to generate priors groups from a pybraincompare.ontology.tree object
output as pickle objects. This is done because it is ideal to calculate priors in a cluster environment.

INPUTS:

tree: a dictionary of nodes, with base nodes matching a particular pattern assumed to be image (.nii.gz) files.
standard_mask: standard image mask that images are registered to
output_folder: a folder path to save priors images
input_folder: the folder of images to be matched to the nodes of the tree.
pattern: the pattern to match to find the base image nodes. Default is a number of any length [neurovault image primary keys].
image_pattern: a regular expression to find image files in images_folder. Default will match any number of leading zeros, any number, and any extension.
node_pattern: a regular expression to find image nodes in the tree, matched to name

OUTPUT: a pickle with the following

pbc_priors_groups_trm_12345.pkl
group["nid"] = "trm_12345"
group["in"] = ["path1","path2",..."pathN"]
group["out"] = ["path3","path4",..."pathM"]
group["meta"]: meta data for the node
group["range_table"]: a data frame of ranges with "start" and "stop" to calculate
                      the range is based on the mins and max of the entire set of images

'''

def priors_groups_from_tree(tree,standard_mask,input_folder,image_pattern="[0]+%s[.]",
                            output_folder=None,node_pattern="[0-9]+",):

    # Find all nodes in the tree, match to images in folder
    nodes = get_node_fields(tree,field="name",nodes=[])
    contender_files = glob("%s/*" %input_folder)

    # Images will match the specified pattern
    find_nodes = re.compile(node_pattern)
    image_nodes = numpy.unique([node for node in nodes if find_nodes.match(node)]).tolist()

    # Node names must now be matched to files
    file_lookup = dict()
    file_names = [os.path.split(path)[-1] for path in contender_files]
    for node in image_nodes:
        find_file = re.compile(image_pattern %node)
        idx = [file_names.index(x) for x in file_names if find_file.match(x)]
        if len(idx) > 1:
            raise ValueError("ERROR: found %s images that match pattern %s." %len(idx),find_file.pattern)
        elif len(idx) == 0:
            print "Did not find file for %s, will not be included in analysis." %(node)
        else:
            file_lookup[node] = contender_files[idx[0]]

    # Use pandas dataframe to not risk weird dictionary iteration orders
    files = pandas.DataFrame(file_lookup.values(),columns=["path"])
    files.index = file_lookup.keys()
 
    # The remaining nodes in the tree (that are not images) will have a RI score
    concept_nodes = [x for x in nodes if x not in image_nodes] 

    # create table of voxels for all images (the top node)
    mr = get_images_df(file_paths=files.path,mask=standard_mask)
    mr.index = files.index

    range_table = make_range_table(mr)

    # PRIORS GROUPS ----------------------------------------------------
    # Find priors groups for image sets at each node (**node names must be unique) 
    # This is images at (and in lower levels) of node vs. everything else
    # will be used to calculate p[activation in range | region (voxel)]

    priors_groups = []

    for concept_node in concept_nodes:
        node = get_node_by_name(tree,concept_node)
        node_id = node["nid"] # for save image
        node_meta = node["meta"]
        if node:
            all_children = get_node_fields(node,"name",[])
            children_in = [child for child in all_children if child in files.index]
            children_out = [child for child in files.index if child not in children_in]
            if len(children_in) > 0 and len(children_out) > 0:
                print "Generating priors group for concept node %s" %(concept_node)
                group = {"in": files.path.loc[children_in].tolist(),
                         "out": files.path.loc[children_out].tolist(),
                         "range_table": range_table,
                         "meta": node_meta,
                         "nid": node_id,
                         "name": concept_node}                

                priors_groups.append(group)
                if output_folder != None:
                    pickle.dump(group,open("%s/pbc_priors_group_%s.pkl" %(output_folder,node_id),"wb"))

    return priors_groups

"""
Generate a table of ranges, in format:
               start  stop
[-28.0,-27.5]  -28.0 -27.5
[-27.5,-27.0]  -27.5 -27.0
[-27.0,-26.5]  -27.0 -26.5
[-26.5,-26.0]  -26.5 -26.0

from a table of values, where images/objects are expected in rows, 
and regions/voxels in columns

ranges, if defined, should be a list of lists of ranges to
extract. eg, [[start,stop],[start,stop]] where start is the min, stop is max

The absolute min and max are used to generate a table of ranges
in the format above from min to max

"""
def make_range_table(mr,ranges=None):

    range_table = pandas.DataFrame(columns=["start","stop"])

    if ranges:
        if not isinstance(ranges,list):
            raise ValueError("ERROR: ranges should be a list of ranges [[start,stop],[start,stop]]")    
        for range_group in ranges:
           if not isinstance(range_group,list) or len(range_group) != 2:
               raise ValueError("ERROR: ranges should be a list of ranges [[start,stop],[start,stop]]")    
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

"""
save_priors_df

will calculate priors and save to a pandas df pickle

nid: a unique identifier, typically a node ID from a pybraincompare.ontology.tree
in_images: a list of files for the "in" group relevant to some concept
out_images: the rest
standard_mask: the standard mask images are in space of
output_folder: folder to save priors images
range_table: a data frame of ranges with "start" and "stop" to calculate
             the range is based on the mins and max of the entire set of images
             can be generated with pybraincompare.inference.make_range_table

OUTPUT:
pbc_priors_trm12345_df_in.pkl
EACH VOXEL IS p(activation in voxel is in threshold)

"""

def save_priors_df(nid,in_images,out_images,standard_mask,output_folder,range_table):
    
    # Read all images into one data frame
    if len(numpy.intersect1d(in_images,out_images)) > 0:
        raise ValueError("ERROR: in_images and out_images should not share images!")
    all_images = in_images + out_images
    mr = get_images_df(file_paths=all_images,mask=standard_mask)
    mr.index = all_images
    in_subset = mr.loc[in_images]
    out_subset = mr.loc[out_images] 
    priors_in = calculate_regional_priors_in_ranges(in_subset,range_table)         
    priors_out = calculate_regional_priors_in_ranges(out_subset,range_table)
    outfile_out = "%s/pbc_priors_%s_df_out.pkl" %(output_folder,nid)
    outfile_in = "%s/pbc_priors_%s_df_in.pkl" %(output_folder,nid)
    priors_in.to_pickle(outfile_in)
    priors_out.to_pickle(outfile_out)
    return {"out":outfile_out,"in":outfile_in}


"""
save_priors_nii

save a nii image for each threshold (column) across all voxels (rows)

input_pkl: the input pickle with all priors saved by pybraincompare.ontology.inference.save_priors_df
output_folder: folder for output nifti, one per threshold range

OUTPUT:
pbc_priors_trm12345_df_in_[start]_[stop].nii
EACH VOXEL IS p(activation in voxel is in threshold) for group [in or out]

"""

def save_priors_nii(input_pkl,output_folder,standard_mask):

    priors = pandas.read_pickle(input_pkl)
    ranges = priors.columns.tolist()
    standard_brain = nibabel.load(standard_mask)

    for range_group in ranges:
        empty_nii = numpy.zeros(shape=standard_brain.shape)
        range_group_str = range_group.replace(",","_to_").replace("[","").replace("]","")
        probs = priors[range_group]
        empty_nii[standard_brain.get_data()!=0] = probs
        out_nii = nibabel.Nifti1Image(empty_nii,affine=standard_brain.get_affine())
        nibabel.save(out_nii,"%s/pbc_priors_%s_df_in.nii.gz" %(output_folder,range_group_str))

'''
calculate_regional_priors_in_ranges: Function to calculate priors from a regionally-based df for ranges of values

region_df: a pandas data frame with voxels/regions in columns, images in rows
range_df: a pandas data frame with columns ["start","stop"], 
          and each row corresponding to a particular range of values
'''

def calculate_regional_priors_in_ranges(region_df,ranges_df):
    # A table of priors, columns --> thresholds, rows --> regions)
    priors = pandas.DataFrame(columns=ranges_df.index)  
    for row in ranges_df.iterrows(): 
        # Nan means that value does not pass
        bool_df = region_df[(region_df >= row[1].start) & (region_df <=row[1].stop)]    
        # [Numerator] Count the non-NaN values in each column, add 1 for laplace smoothing
        # [Denominator] sum(numerator with no laplace) + V (words in vocabulary --> regions/voxels)
        # [Overall] probability that the image voxel (region) is in the range given entire image set
        numerator = (bool_df.shape[0] - bool_df.isnull().sum())
        numerator_laplace_smoothed = numerator + 1
        denominator = numpy.sum(numerator) + bool_df.shape[1]
        priors[row[0]] = numerator_laplace_smoothed / denominator
    return priors


'''
calculate_reverse_inferences_threshes: 

return reverse inference value for each threshold in priors matrix

# Reverse Inference Calculation ------------------------------------------------------------------
# P(node mental process|activation) = P(activation|mental process) * P(mental process)
# divided by
# P(activation|mental process) * P(mental process) + P(A|~mental process) * P(~mental process)
# P(activation|mental process): my voxelwise prior map

p_in: priors in table, columns are thresholds, rows are voxels
p_out: priors out table, ""  ""
in_count: number of brain images used to generate p_in table
out_count: number of brain images used to generate p_out table

'''
def calculate_reverse_inference_threshes(p_in,p_out,in_count,out_count):
    total = in_count + out_count # total number of nifti images
    p_process_in = float(in_count) / total   # percentage of niftis in
    p_process_out = float(out_count) / total # percentage out
    
    # If we multiply, we will get 0, so we take sum of logs
    p_in_log = numpy.log(p_in)
    p_out_log = numpy.log(p_out)
    numerators = p_in_log.sum(axis=0) * p_process_in
    denominators = (p_in_log.sum(axis=0) * p_process_in) + (p_out_log.sum(axis=0) * p_process_out)
    return (numerators / denominators)

'''
calculate_reverse_inference: Function to return reverse inference value based on particular thresholds of a brain stat map (or average of the node set) - this will return one value!

mrtable: should be a table, with images in rows, and voxels/regions in columns
         if there is more than one image, a mean will be used
range_table: will be used to define ranges of interest. The image will be thresholded for these ranges

'''

def calculate_reverse_inference(mrtable,range_table,p_in,p_out,in_count,out_count):
    
    if not isinstance(mrtable,pandas.core.frame.DataFrame):
        mrtable = pandas.DataFrame(mrtable)

    # If we are given a DataFrame with multiple rows, take mean

    total = in_count + out_count # total number of nifti images
    p_process_in = float(in_count) / total   # percentage of niftis in
    p_process_out = float(out_count) / total # percentage out

    # If we multiply, we will get 0, so we take sum of logs
    if mrtable.shape[1]>1:
        mrtable = pandas.DataFrame(mrtable.mean())

    # For each ACTUAL voxel value, assign to its threshold
    stat_map_levels = pandas.DataFrame(columns=mrtable.columns,index=mrtable.index)
    for row in range_table.iterrows():
        stat_map_levels[(mrtable >= row[1].start) & (mrtable <=row[1].stop)] = row[0]

    # Now use actual threshold labels to choose the appropriate probability values for each voxel
    # I need advice how to make this faster, and this should be a separate function
    p_in_vector = []  # a vector of probability values, using p_in as a lookup
    p_out_vector = []

    # For each threshold
    for v in range(0,stat_map_levels.shape[0]):
        level = stat_map_levels[0][v]
        # Look up the levels, append to our lists
        p_in_vector.append(p_in.loc[v,level])
        p_out_vector.append(p_out.loc[v,level])

    # Convert to logs
    p_in_log = numpy.log(p_in_vector)
    p_out_log = numpy.log(p_out_vector)
    numerator = p_in_log.sum(axis=0) * p_process_in
    denominator = (p_in_log.sum(axis=0) * p_process_in) + (p_out_log.sum(axis=0) * p_process_out)
    return (numerator / denominator)
