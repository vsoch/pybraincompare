'''
graph.py: part of pybraincompare package
Functions to work with ontology graphs

'''
import sys
import json
from pybraincompare.template.templates import get_package_dir
from JSONEncoder import Node, NodeDict, NodeJSONEncoder


# This function will "grab" a node by the name ( a subset of the tree )
def locate_by_name(myjson,name):
    if myjson.get('name',None) == name:
        return myjson
    for child in myjson.get('children',[]):
        result = locate_by_name(child,name)
        if result is not None:
            return result
    return None

# This function will get all the names of the nodes
def get_node_names(myjson,names=[]):
    if myjson.get('name',None) == None:
        return names
    else: 
        names.append(myjson.get('name'))
  for child in myjson.get('children',[]):
      names = get_node_names(child,names)
      if not names: 
          return None
  return names

# This function will return all nifti images for some json tree
def get_nifti_names(myjson,nii_files=[]):
    import re
    expression = re.compile(".nii.gz")
    if myjson.get('name',None) == None:
        return nii_files
    else: 
        if expression.search(myjson.get('name')):
            nii_files.append(myjson.get('name'))
        for child in myjson.get('children',[]):
            nii_files = get_nifti_names(child,nii_files)
        if not nii_files: return None
    return nii_files
