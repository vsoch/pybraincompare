'''
inference.py: part of pybraincompare package
Functions to calculate reverse inference

'''

'''
calculate_regional_priors_in_ranges: Function to calculate priors from a regionally-based df for ranges of values

ranges_df should have columns ["start","stop"]
ranges_df.index (row names) should correspond to region name!
'''
def calculate_regional_priors_in_ranges(region_df,ranges_df):
    # A table of priors, columns --> thresholds, rows --> regions)
    priors = pd.DataFrame(columns=ranges_df.index)  # defined for images in nodeg
    for row in ranges_df.iterrows(): 
        # Nan means that value does not pass
        bool_df = region_df[(region_df >= row[1].start) & (region_df <=row[1].stop)]    
        # [Numerator] Count the non-NaN values in each column, add 1 for laplace smoothing
        # [Denominator] sum(numerator with no laplace) + V (words in vocabulary --> regions/voxels)
        # [Overall] probability that the image voxel (region) is in the range given entire image set!
        numerator = (bool_df.shape[0] - bool_df.isnull().sum())
        numerator_laplace_smoothed = numerator + 1
        denominator = np.sum(numerator) + bool_df.shape[0]
        priors[row[0]] = numerator_laplace_smoothed / denominator
    return priors

'''
calculate_reverse_inferences_threshes: Function to return reverse inference value for each threshold in priors matrix
'''
def calculate_reverse_inference_threshes(p_in,p_out,num_in,num_out):
    import numpy as np
    total = in_count + out_count # total number of nifti images
    p_process_in = float(in_count) / total   # percentage of niftis in
    p_process_out = float(out_count) / total # percentage out
    
    # If we multiply, we will get 0, so we take sum of logs
    p_in_log = np.log(p_in)
    p_out_log = np.log(p_out)
    numerators = p_in_log.sum(axis=0) * p_process_in
    denominators = (p_in_log.sum(axis=0) * p_process_in) + (p_out_log.sum(axis=0) * p_process_out)
    return (numerators / denominators)

'''
calculate_reverse_inference: Function to return reverse inference value based on particular thresholds of a brain stat map (or average of the node set) - this will return one value!
'''
def calculate_reverse_inference(stat_map,ranges_df,p_in,p_out,num_in,num_out):
    import numpy as np, pandas as pd
    total = in_count + out_count # total number of nifti images
    p_process_in = float(in_count) / total   # percentage of niftis in
    p_process_out = float(out_count) / total # percentage out
    # If we multiply, we will get 0, so we take sum of logs
    # For each ACTUAL voxel value, assign to its threshold (all thresholds should be represented)
    stat_map_levels = stat_map.copy()
    for row in ranges_df.iterrows():
        stat_map_levels.loc[(stat_map >= row[1].start) & (stat_map <=row[1].stop)] = row[0]
    # BUG WILL BE CHANGED: For now we will put values slightly above threshold in upper/lower - this needs
    idx_upper =  [x for x in range(0,len(stat_map_levels)) if (stat_map_levels[x] not in range_table.index) and stat_map_levels[x] > 3.0]
    idx_lower =  [x for x in range(0,len(stat_map_levels)) if (stat_map_levels[x] not in range_table.index) and stat_map_levels[x] < -8.0]
    stat_map_levels.loc[idx_upper] = "[2.5,3.0]"
    stat_map_levels.loc[idx_lower] = "[-8.0,-7.5]"
    # Now use actual threshold labels to choose the appropriate probability values for each voxel
    # I need advice how to make this faster, and this should be a separate function
    p_in_vector = []; p_out_vector = [];
    for v in range(0,len(stat_map_levels)):
        level = stat_map_levels[v] 
        p_in_vector.append(p_in.loc[v,level])
        p_out_vector.append(p_out.loc[v,level]) 
    p_in_log = np.log(p_in_vector)
    p_out_log = np.log(p_out_vector)
    numerator = p_in_log.sum(axis=0) * p_process_in
    denominator = (p_in_log.sum(axis=0) * p_process_in) + (p_out_log.sum(axis=0) * p_process_out)
    return (numerator / denominator)
