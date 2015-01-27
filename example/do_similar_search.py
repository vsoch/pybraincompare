# This will generate an interactive web interface to find similar images
from template.visual import view
from compare.compare import similarity_search
from glob import glob
import pandas

# This is a square matrix of image comparisons (pearson correlations)
# Row and column names should correspond to image unique IDs
corr_df = pandas.read_pickle("/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/example/data/pearson_corr.pkl")

# Here are pre-generated png images
png_images = glob("/home/vanessa/Packages/vagrant/neurovault/image_data/images/1/*.png") + glob("/home/vanessa/Packages/vagrant/neurovault/image_data/images/2/*.png")

# Create a list of tags for each image
tags = [["Z","brain"],["Z","brain"],["brain"],["Z","brain"],["Z","brain"]]

# Tags and png paths should be appended to same data frame, so image ids are associated with both
corr_df["png"] = png_images
corr_df["tags"] = tags

# compare URL prefix to go from linked images, undefined will link to png image
compare_url = "http://www.neurovault.org/compare" # format will be prefix/[query_id]/[other_id]
image_url = "http://www.neurovault.org/image" # format will be prefix/[other_id]

# Here is the query image
query = png_images[0]

# You can optionally add image names
image_names = ["image 1","image 2","image 3","image 4","image 5"]

# Currently only supporting generating similarity search for pre-computed similarity data frame
html_snippet = similarity_search(corr_df=corr_df,button_url=compare_url,image_url=image_url,query=query,image_names=image_names)

# Show in browser
view(html_snippet)
