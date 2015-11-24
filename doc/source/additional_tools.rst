Additional Tools
================

QA Report
'''''''''

Pybraincompare can also generate a QA report for a set of images. This is useful to quickly run QA, and then serve the result / send to someone to easily see and understand the data. An `example is provided <vbmis.com/bmi/project/qa>`_ along with `this script <https://github.com/vsoch/pybraincompare/blob/master/example/run_quality_analysis.py>`_

::

    #!/usr/bin/env python2

    from glob import glob
    from pybraincompare.report.webreport import run_qa

    # Here is a set of 144 images, these are 9 openfmri studies in Neurovault, resampled to MNI 2mm
    mrs = glob("/home/vanessa/Documents/Work/BRAINMETA/IMAGE_COMPARISON/mr/resampled/*.nii.gz")

    # Run quality analysis
    outdir = "/home/vanessa/Desktop/test"
    run_qa(mrs,software="FSL",html_dir=outdir,voxdim=[2,2,2],outlier_sds=6,investigator="Vanessa",nonzero_thresh=0.25)

    # For large datasets (where memory is an issue) you can set calculate_mean_histogram=False


Connectogram
''''''''''''

Generate a connectogram d3 visualization from a square connectivity matrix `demo <http://vbmis.com/bmi/share/neurovault/connectogram.html>`_ and `script <https://github.com/vsoch/pybraincompare/blob/master/example/make_connectogram.py>`_


::
   
    from pybraincompare.compare.network import connectogram
    from pybraincompare.template.visual import view
    import pandas

    # A square matrix, tab separated file, with row and column names corresponding to node names
    connectivity_matrix = "data/parcel_matrix.tsv"

    parcel_info = pandas.read_csv("data/parcels.csv")
    networks = list(parcel_info["Community"])
    # should be in format "L-1" for hemisphere (L or R) and group number (1..N)
    groups = ["%s-%s" %(parcel_info["Hem"][x],parcel_info["ID"][x]) for x in range(0,parcel_info.shape[0])]

    # A threshold value for the connectivity matrix to determine neighbors, eg, a value of .95 means we only keep top 5% of positive and negative connections, and the user can explore this top percent
    threshold = 0.99
    html_snippet = connectogram(matrix_file=connectivity_matrix,groups=groups,threshold=threshold,network_names=networks)

    view(html_snippet)
