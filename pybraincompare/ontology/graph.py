#!/usr/bin/env python

'''
graph.py: part of pybraincompare package
Functions to work with ontology graphs

'''
import re
import sys
import json
import pandas
import UserDict
from pybraincompare.template.templates import get_package_dir

class Node(object):
    def __init__(self, nid, parent, name, meta=None):
        self.nid = nid
        self.parent = parent
        self.children = []
        self.name = name
        self.meta = [meta] # should be dictionary!

def get_json(nodes,category_groups=False):
    tree = dict()
    # Make an empty node object for each node
    for node in nodes:
        tree[node.nid] = {"nid":node.nid, "name":node.name, "meta":node.meta,"children":[]}
    # Add base nodes to the queue
    expression = re.compile("node_*")
    queue = [child for child in nodes if expression.search(child.nid)]
    remainder = [child for child in nodes if child not in queue]

    while queue:
        current = queue.pop()
        # Get json of node
        node = tree[current.nid]
        # Remove child from the tree
        new_tree = dict() # This has to be done for python 2.6 support
        for k,v in tree.iteritems():
           if k != current.nid:
               new_tree[k] = v
        tree = new_tree
        # Append as child to all parent json
        parents = current.parent
        for parent in parents:
            if parent != "None":
                tree[parent]["children"].append(node)

    while remainder:
        current = remainder.pop()        
        # Get json of node
        node = tree[current.nid]
        # Append as child to all parent json
        parents = current.parent
        for parent in parents:
            if parent != "None":
                tree[parent]["children"].append(node)

    # For now, just remove first level of children that don't have children
    root = tree["1"]
    new_children = []
    for child in root["children"]:
        if child["children"]:
            new_children.append(child)

    # Finally, put each of children into its "category"
    if category_groups == True
        category_lookup = {'ctp_C1':'Perception','ctp_C10':'Motivation','ctp_C2':'Attention',
                       'ctp_C3':'Reasoning And Decision Making',
                       'ctp_C4':'Executive-Cognitive Control',
                       'ctp_C5':'Learning and Memory',
                       'ctp_C6':'Language','ctp_C7':'Action','ctp_C8': 'Emotion',
                       'ctp_C9':'Social Function'}

        category_nodes = dict()
        for category,name in category_lookup.iteritems():
            category_nodes[category] = {"nid":category, "name":name, "meta":[],"children":[]}

        # Nodes without categories will just be orphans
        orphans = []
        for child in new_children:
            if child["meta"][0]["category"] in category_nodes:
                category_nodes[child["meta"][0]["category"]]["children"].append(child)
            else: 
                orphans.append(child)    

        # Put them all into the same house!
        for category,category_node in category_nodes.iteritems():
            orphans.append(category_node)

    else:
        orphans = new_children

    root["children"] = orphans

    return root


# Utils
def check_pandas_columns(df,column_names):
    for column_name in column_names:
        if column_name not in df.columns:
            raise ValueError('column %s is missing from relationship table.' %(column_name))
            
def find_circular_reference(relationship_table):
    unique_nodes = relationship_table.id.unique().tolist()
    for node in unique_nodes:
        parents = relationship_table.parent[relationship_table.id==node].tolist()
        # Check to see that parent is not also a child of current node
        for parent in parents:
            parent_parents = relationship_table.parent[relationship_table.id==parent].tolist()
            if node in parent_parents:
                raise ValueError("ERROR: circular reference between %s and %s" %(node,parent))
    

# This function will "grab" a node by the name ( a subset of the tree )
def get_node_by_name(myjson,name):
    if myjson.get('name',None) == name:
        return myjson
    for child in myjson.get('children',[]):
        result = get_node_by_name(child,name)
        if result is not None:
            return result
    return None

# This function will get all the names of the nodes
def get_node_fields(myjson,field="name",nodes=[]):
    if myjson.get(field,None) == None:
        return nodes
    else: 
        nodes.append(myjson.get(field))
        for child in myjson.get('children',[]):
            nodes = get_node_fields(myjson=child,field=field,nodes=nodes)
    if not nodes: 
          return None
    return nodes
