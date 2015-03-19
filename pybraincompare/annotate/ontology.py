import sys
import json
from pybraincompare.template.templates import get_package_dir, get_template, add_string
from JSONEncoder import Node, NodeDict, NodeJSONEncoder

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

'''named_ontology_tree_from_tsv: equivalent to the above, except with structured "name", "id" and "children" fields. Format should be:

id	parent	name
1	none BRAINMETA
2	1	RESPONSE_INHIBITION
3	1	RISK_SEEKING
4	2	DS000009

'''
def named_ontology_tree_from_tsv(relationship_table,output_json=None,meta_data=None):
  nodes = []

  if meta_data:
    with open(relationship_table) as f:
      for row in f.readlines()[1:]:
        meta = dict()
        nid, parent, name = row.strip().split()
        if name in meta_data.keys():
          meta[name] = meta_data[name]
        else: meta[name] = ""
        nodes.append(Node(nid, parent, name, meta))
  else:
    with open(relationship_table) as f:
      for row in f.readlines()[1:]:
        nid, parent, name = row.strip().split()
        nodes.append(Node(nid, parent, name))

  nodeDict = NodeDict()
  nodeDict.addNodes(nodes)

  rootNode = [node for nid, node in nodeDict.items() if node.parent == "none"]
  data_structure = NodeJSONEncoder().encode(rootNode[0])

  if output_json:
    filey = open(output_json,"wb")
    filey.writelines(data_structure)
    filey.close()
 
  return data_structure

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

