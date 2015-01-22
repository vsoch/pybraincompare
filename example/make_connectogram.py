# Make a connectogram d3 visualization from a square connectivity matrix

from compare.network import connectogram
from template.visual import view
import pandas

# A square matrix, tab separated file, with row and column names corresponding to node names
connectivity_matrix = "example/data/parcel_matrix.tsv"

parcel_info = pandas.read_csv("example/data/parcels.csv")
networks = list(parcel_info["Community"])
# should be in format "L-1" for hemisphere (L or R) and group number (1..N)
groups = ["%s-%s" %(parcel_info["Hem"][x],parcel_info["ID"][x]) for x in range(0,parcel_info.shape[0])]

# A threshold value for the connectivity matrix to determine neighbors, eg, a value of .95 means we only keep top 5% of positive and negative connections, and the user can explore this top percent
threshold = 0.99

html_snippet = connectogram(matrix_file=connectivity_matrix,groups=groups,threshold=threshold)

view(html_snippet)
