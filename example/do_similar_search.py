# This will generate an interactive web interface to find similar images
from template.visual import view
from compare.compare import similarity_search
from glob import glob
import pandas


# Here are pre-generated png images, order should correspond to order of your data
png_paths = glob("/home/vanessa/Packages/vagrant/neurovault2/image_data/images/1/*.png") + glob("/home/vanessa/Packages/vagrant/neurovault2/image_data/images/2/*.png")

# Create a list of tags for each image, same order as data
tags = [["Z","brain"],["Z","brain"],["brain"],["Z","brain"],["Z","brain"],["Other"]]

# compare URL prefix to go from linked images, undefined will link to png image
compare_url = "http://www.neurovault.org/compare" # format will be prefix/[query_id]/[other_id]
image_url = "http://www.neurovault.org/image" # format will be prefix/[other_id]

# IDS that will fill in the url paths above
image_ids = [1,2,3,4,5,6]

# Here is the query png image and ID
query_png = png_paths[0]
query_id = image_ids[0]

# You can optionally add image names
image_names = ["image 1","image 2","image 3","image 4","image 5","image 6"]

# Calculate your scores however you wish
image_scores = [1,0.87,0.30,0.2,0.9,0.89]

# Calculate similarity search, get html
html_snippet = similarity_search(image_scores=image_scores,tags=tags,png_paths=png_paths,
                                button_url=compare_url,image_url=image_url,query_png=query_png,
                                query_id=query_id,image_names=image_names,image_ids=image_ids)

# Show in browser
view(html_snippet)
