'''
plots.py: part of pybraincompare package
Functions to plot stuff

'''
from nilearn.plotting import plot_glass_brain, plot_roi, plot_img, plot_anat, plot_stat_map
from colors import random_colors
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from matplotlib.figure import Figure
from matplotlib.gridspec import GridSpec
from pylab import cm
import numpy as np
import pylab as P


# Plot brain images

"""Make roi (mask) image"""
def make_roi_image(nifti_file,png_img_file=None):
  nifti_file = str(nifti_file)
  mask_brain = plot_roi(nifti_file)
  if png_img_file:    
    mask_brain.savefig(png_img_file)
  plt.close('all')
  return mask_brain


"""Make statmap image"""
def make_stat_image(nifti_file,png_img_file=None):
  nifti_file = str(nifti_file)
  brain = plot_stat_map(nifti_file)
  if png_img_file:    
    brain.savefig(png_img_file)
  plt.close('all')
  return brain


"""Make anat image"""
def make_anat_image(nifti_file,png_img_file=None):
  nifti_file = str(nifti_file)
  brain = plot_anat(nifti_file)
  if png_img_file:    
    brain.savefig(png_img_file)
  plt.close('all')
  return brain


"""Make glassbrain image, optional save image to png file (not vector)"""
def make_glassbrain_image(nifti_file,png_img_file=None):
  nifti_file = str(nifti_file)
  glass_brain = plot_glass_brain(nifti_file)
  if png_img_file:    
    glass_brain.savefig(png_img_file)
  plt.close('all')
  return glass_brain


'''Get histogram data for an image (for d3)'''
def get_histogram_data(data,width=12,height=4,color=None,ylabel="frequency",xlabel="map intensity value bins",title="Histogram of Intensity Values for Image",bins=25):
  if not color: color = random_colors(1)[0]
  data = data.flatten()
  data = np.array(data)[np.isnan(data)==False]
  n, bins, patches = P.hist(data, bins, normed=1, histtype='stepfilled')
  membership = np.digitize(data,bins)
  counts = [membership.tolist().count(x) for x in range(1,len(bins))]
  return {"n":n,"bins":bins,"patches":patches,"counts":counts}


'''plot histogram (not just return data)
adopted from chrisfilo https://github.com/chrisfilo/mriqc'''
def plot_histogram(masked_data,remove_zero=False,title=None,line_value=None,xlabel=None,width=11,height=4,png_img_file=None,threshold=0.001):
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

'''plot histogram (not just return data) and include normal distribution outline
TODO: add normal to this!
'''
def plot_histogram_with_normal(masked_data,remove_zero=False,title=None,line_value=None,xlabel=None,width=11,height=4,png_img_file=None,threshold=0.001):
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

'''from chrisfilo https://github.com/chrisfilo/mriqc'''
def plot_vline(cur_val, label, ax):
    ax.axvline(cur_val)
    ylim = ax.get_ylim()
    vloc = (ylim[0] + ylim[1]) / 2.0
    xlim = ax.get_xlim()
    pad = (xlim[0] + xlim[1]) / 100.0
    ax.text(cur_val - pad, vloc, label, color="blue", rotation=90, verticalalignment='center', horizontalalignment='right')
