'''
image.py: part of pybraincompare package
Functions for static images

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

'''from chrisfilo https://github.com/chrisfilo/mriqc'''
def plot_vline(cur_val, label, ax):
    ax.axvline(cur_val)
    ylim = ax.get_ylim()
    vloc = (ylim[0] + ylim[1]) / 2.0
    xlim = ax.get_xlim()
    pad = (xlim[0] + xlim[1]) / 100.0
    ax.text(cur_val - pad, vloc, label, color="blue", rotation=90, verticalalignment='center', horizontalalignment='right')
