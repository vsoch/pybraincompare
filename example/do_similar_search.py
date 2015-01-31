# This will generate an interactive web interface to find similar images
from template.visual import view
from compare.compare import similarity_search
from glob import glob
import pandas


# Here are pre-generated png images, order should correspond to order of your data
png_images = glob("/home/vanessa/Packages/vagrant/neurovault/image_data/images/1/*.png") + glob("/home/vanessa/Packages/vagrant/neurovault/image_data/images/2/*.png")

# Create a list of tags for each image, same order as data
tags = [["Z","brain"],["Z","brain"],["brain"],["Z","brain"],["Z","brain"]]

# Here is the query image
query = png_images[0]

# compare URL prefix to go from linked images, undefined will link to png image
compare_url = "http://www.neurovault.org/compare" # format will be prefix/[query_id]/[other_id]
image_url = "http://www.neurovault.org/image" # format will be prefix/[other_id]

# You can optionally add image names
image_names = ["image 1","image 2","image 3","image 4","image 5"]

# This is a square matrix of image comparisons (pearson correlations)
# Row and column names correspond to image unique IDs
corr_df = pandas.read_pickle("/home/vanessa/Documents/Dropbox/Code/Python/pybraincompare/example/data/pearson_corr.pkl")

# We select the column of the query image we are interested in, now this is a pandas series
corr_df = corr_df[2]

# Calculate similarity search, get html
html_snippet = similarity_search(data=corr_df,tags=tags,png_paths=png_images,button_url=compare_url,image_url=image_url,query=query,image_names=image_names)

# Show in browser
view(html_snippet)
