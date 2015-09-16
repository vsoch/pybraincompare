'''
tree.py: part of pybraincompare package
Functions to visualize ontology trees

'''
import sys
import json
from pybraincompare.template.templates import get_package_dir, get_template, add_string
from pybraincompare.ontology.graph import Node, get_json, check_pandas_columns, find_circular_reference

# Annotate and visualize data with an ontology
'''ontology_tree_from_tsv: create annotation json for set of images to visualize hierarchy, with nodes being names/counts for each category.  Image table should be organized in the following format:

ROOT    CONCEPT_A    CONTRAST_1    image_file_1
ROOT    CONCEPT_B    CONTRAST_1    image_file_2
ROOT    CONCEPT_D    CONTRAST_2    image_file_3

Each name corresponds to whatever the node is called, with the final column having the image names.
NOTE: This format is not currently compatible with any d3 visualizations, just an option for data export!
'''
def ontology_tree_from_tsv(relationship_table,output_json=None):
    data_structure = {}
    for line in open(relationship_table,'r'):
        data = line.strip().split("\t")

        current = data_structure
        for item in data[:-1]:
            if not current.has_key(item):
                current[item] = {}
            current = current[item]
        if not current.has_key(data[-1]):
            current[data[-1]] = 1
        else:
            current[data[-1]] += 1
    if output_json:
        with open(output_json,"wb") as fp:
            json.dump(data_structure,fp)

    return data_structure

'''named_ontology_tree_from_tsv: generate a tree from a data structure with the following format:

relationship_table: either a file or pandas data frame with this format
delim: the delimiter use to separate values
meta_data [OPTIONAL]: if defined, should be a dictionary of dictionaries, with:
      key = the node id
      value = a dictionary of meta data. For example:

      {
        "trm_12345":{"defined_by":"squidward","score":1.2},
        "node_54321":{"date":"12/15/15"}
      }

Meta data will be shown via mouseover of the nodes in the tree.

id	parent	name
1	none BRAINMETA
2	1	RESPONSE_INHIBITION
3	1	RISK_SEEKING
4	2	DS000009

'''
def named_ontology_tree_from_tsv(relationship_table,output_json=None,meta_data=None,delim="\t"):
    nodes = []

    if not isinstance(relationship_table,pandas.DataFrame):
        relationship_table = pandas.read_csv(relationship_table,sep="\t")

    # check for correct columns and circular references
    check_pandas_columns(df=relationship_table,column_names=["id","name","parent"])
    find_circular_reference(relationship_table)

    # Generate nodes
    unique_nodes = relationship_table.id.unique().tolist()
    print "%s unique nodes found." %(len(unique_nodes))
    for node in unique_nodes:
        parents = relationship_table.parent[relationship_table.id==node].tolist()
        name = relationship_table.name[relationship_table.id==node].unique().tolist()
        if len(name) > 1:
            raise ValueError("Error, node %s is defined with multiple names." %node)
        meta = ""
        if meta_data:
           if node in meta_data:
               meta = meta_data[node]
        nodes.append(Node(node, parents, name[0], meta))

    # Generate json
    graph = get_json(nodes)

    if output_json:
        with open(output_json, 'wb') as outfile:
            json.dump(graph, outfile)
 
    return graph

'''Render d3 of ontology tree, return html with embedded data'''
def make_ontology_tree_d3(data_structure):
    temp = get_template("ontology_tree")
    temp = add_string({"INPUT_ONTOLOGY_JSON":data_structure},temp)
    return temp

'''Render d3 of ontology tree, return html with embedded data'''
def make_reverse_inference_tree_d3(data_structure):
    temp = get_template("reverse_inference_tree")
    temp = add_string({"INPUT_ONTOLOGY_JSON":data_structure},temp)
    return temp
