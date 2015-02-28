# Functions for visualization parameters
import matplotlib.pyplot as plt
import numpy as np
import random
import re

'''Animate subplots from current matplotlib figure'''
#%config InlineBackend.figure_format = 'svg'
def animate_figure():
  with make_tmp_folder() as tmp_dir:  
    # Write to temporary file, read in svg
    tmp_file = "%s/pybraind3.svg" %(tmp_dir)
    plt.savefig(tmp_file)
    tmp = open(tmp_file,"rb")
    content = tmp.readlines()
    tmp.close()
    # Find the first mention of svg, the start
    expression = re.compile("<svg")
    matches = [expression.search(x) for x in content] 
    match =[x for x in range(0,len(matches)) if matches[x]][0]+1
    content = content[match:len(content)]
    [x for x in [expression.search(x) for x in content] if x]
    # TODO: write code here to put into animation...
