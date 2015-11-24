Semantic Image Comparison
=========================

Semantic image comparison means comparing images by way of texy data that is associated with them, for example meta data, or in the case of functional neuroimaging, using an ontology like the `Cognitive Atlas <http://www.cognitiveatlas.org>`_ to associate images with contrasts and cognitive concepts. Pybraincompare has several methods for reverse inference that will be better documented with a publication, and for now, here are examples to generate trees of ontology structures.


Ontology Tree
'''''''''''''
This function will generate an interactive d3 representation of a graph data structure `demo <http://vbmis.com/bmi/share/neurovault/ontology_tree.html>`_ and `script <https://github.com/vsoch/pybraincompare/blob/master/example/make_ontology_tree.py>`_


::

    #!/usr/bin/env python2

    from pybraincompare.ontology.tree import named_ontology_tree_from_tsv
    from pybraincompare.template.visual import view

    # This defines a "mock" ontology for the openfmri proof of concept set - names should be unique
    relationship_table = "data/cogatlas_annotate_triples.tsv"

    # Create a data structure for d3 visualization and data analysis (no output json, specify with output_json=)
    data_structure = named_ontology_tree_from_tsv(relationship_table)
    html_snippet = make_ontology_tree_d3(data_structure)

    # View in browser!
    view(html_snippet)


Reverse Inference Tree
''''''''''''''''''''''

This function will generate an interactive d3 representation of a graph data structure with mouseover tags that show a reverse inference score for a node, `demo <http://vbmis.com/bmi/share/neurovault/reverse_inference.html>`_ and a `script <https://github.com/vsoch/pybraincompare/blob/master/example/make_reverse_inference_tree.py>`_ are available.


::

    #!/usr/bin/env python2

    import pandas as pd
    from pybraincompare.ontology.tree import named_ontology_tree_from_tsv, make_ontology_tree_d3
    from pybraincompare.template.visual import view

    # This defines a "mock" ontology for the openfmri proof of concept set - names should be unique
    relationship_table = "data/cogatlas_annotate_triples.tsv"

    # We want to prepare a dictionary of meta data to correspond to some nodes
    reverse_inference_df = pd.read_csv("data/reverse_inference_scores.tsv",sep="\t")
    reverse_inferences = dict()
    for row in reverse_inference_df.iterrows():
        reverse_inferences[row[1].NODE_GROUP] = row[1].REVERSE_INFERENCE_SCORE

    # Create a data structure for d3 visualization and data analysis (no output json, specify with output_json=)
    data_structure = named_ontology_tree_from_tsv(relationship_table, meta_data = reverse_inferences)
    html_snippet = make_reverse_inference_tree_d3(data_structure)

    # View in browser!
    view(html_snippet)

