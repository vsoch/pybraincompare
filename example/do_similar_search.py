# This will generate an interactive web interface to find similar images
from pybraincompare.template.visual import view
from pybraincompare.compare.search import similarity_search
from glob import glob
import pandas

# Here are pre-generated png images, order should correspond to order of your data
png_paths = glob("/home/vanessa/Packages/vagrant/neurovault/image_data/images/3/*.png")[0:6]

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

# You can optionally add bottom text and top text
image_names = ["image 1","image 2","image 3","image 4","image 5","image 6"]
collection_names = ["collection 1","collection 1","collection 1","collection 1","collection 1","collection 2"]

# Calculate your scores however you wish
image_scores = [1,0.87,0.30,0.2,0.9,0.89]

# Calculate similarity search, get html
html_snippet = similarity_search(image_scores=image_scores,tags=tags,png_paths=png_paths,
                                button_url=compare_url,image_url=image_url,query_png=query_png,
                                query_id=query_id,bottom_text=collection_names,
                                top_text=image_names,image_ids=image_ids)

# Show in browser
view(html_snippet)

# You can also remove JQUERY or BOOTSTRAP, if you are embedding in a page that already has.
remove_scripts = ["JQUERY","BOOTSTRAP"]
html_snippet = similarity_search(image_scores=image_scores,tags=tags,png_paths=png_paths,
                                button_url=compare_url,image_url=image_url,query_png=query_png,
                                query_id=query_id,bottom_text=collection_names,
                                top_text=image_names,image_ids=image_ids,remove_scripts=remove_scripts)
view(html_snippet)
