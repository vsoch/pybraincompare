'''
histogram.py: part of pybraincompare package
Functions for histograms

'''
from pybraincompare.template.templates import get_template, add_string
from pybraincompare.template.visual import view
from nilearn.plotting import plot_glass_brain, plot_roi, plot_img, plot_anat, plot_stat_map
from pybraincompare.compare.mrutils import get_nii_obj
from colors import random_colors
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from pylab import cm
import numpy as np
import pylab as P

'''Get histogram data for an image (for d3)'''
def get_histogram_data(data,width=12,height=4,color=None,ylabel="frequency",xlabel="map intensity value bins",title="Histogram of Intensity Values for Image",bins=25,remove_zeros=True):
  if not color: color = random_colors(1)[0]
  data = data.flatten()
  if remove_zeros == True:
      data = data[data!=0]
  data = np.array(data)[np.isnan(data)==False]
  n, bins, patches = P.hist(data, bins, normed=1, histtype='stepfilled')
  membership = np.digitize(data,bins)
  counts = [membership.tolist().count(x) for x in range(1,len(bins))]
  return {"n":n,"bins":bins,"patches":patches,"counts":counts}


'''make histogram figure
adopted from chrisfilo https://github.com/chrisfilo/mriqc'''
def histogram_image(masked_data,remove_zero=False,title=None,line_value=None,xlabel=None,width=11,height=4,png_img_file=None,threshold=0.001):
  if remove_zero: 
    set1 = np.where(masked_data < threshold)[0]
    set2 = np.where(masked_data > -threshold)[0]
    set3 = np.where(masked_data ==0)[0]
    eliminate =  np.union1d(np.intersect1d(set1,set2),set3)
    masked_data[eliminate] = 0
    masked_data = masked_data[np.where(masked_data!=0)[0]]
  fig = plt.figure(figsize=(width,height))  
  gs = GridSpec(1, 1)
  ax = fig.add_subplot(gs[0, 0])
  sns.distplot(masked_data.astype(np.double), kde=False, bins=100, ax=ax)
  if xlabel: ax.set_xlabel(xlabel)    
  if title: fig.suptitle(title, fontsize='10')
  if line_value: plot_vline(line_val, label, ax=ax)
  if png_img_file: fig.savefig(png_img_file)  
  return fig

'''plot interactive histogram (in browser)'''
def plot_histogram(image,title="Image Histogram",height=400,width=1000,view_in_browser=True,bins=25,remove_zeros=True):
  image = get_nii_obj(image)[0]
  data = image.get_data()
  histogram = get_histogram_data(data,bins=bins,remove_zeros=remove_zeros)
  bins = '"%s"' %('","'.join(["%.2f" %(x) for x in histogram["bins"]]))
  counts = '"%s"' %('","'.join(["%s" %(x) for x in histogram["counts"]]))
  template = get_template("histogram")  
  elements = [{"HISTOGRAM_DATA":counts},
              {"HISTOGRAM_LABELS":bins},
              {"HISTOGRAM_TITLE":title},
              {"HISTOGRAM_HEIGHT":height},
              {"HISTOGRAM_WIDTH":width}]
  for element in elements:
    template = add_string(element,template)      

  if view_in_browser==True:
      view(template)  
  else:
      return template
