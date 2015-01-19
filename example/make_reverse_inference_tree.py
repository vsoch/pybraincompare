#!/usr/bin/env python2

import pandas as pd
from annotate import ontology
from template.visual import view

# This defines a "mock" ontology for the openfmri proof of concept set - names should be unique
relationship_table = "/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/example/data/cogatlas_annotate_triples.tsv"

# We want to prepare a dictionary of meta data to correspond to some nodes
reverse_inference_df = pd.read_csv("/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/example/data/reverse_inference_scores.tsv",sep="\t")
reverse_inferences = dict()
for row in reverse_inference_df.iterrows():
  reverse_inferences[row[1].NODE_GROUP] = row[1].REVERSE_INFERENCE_SCORE

# Create a data structure for d3 visualization and data analysis (no output json, specify with output_json=)
data_structure = ontology.named_ontology_tree_from_tsv(relationship_table, meta_data = reverse_inferences)

html_snippet = ontology.make_reverse_inference_tree_d3(data_structure)

# View in browser!
view(html_snippet)
