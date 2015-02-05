'''
qa.py: part of pybraincompare package
Functions to check quality of statistical maps

'''
import os
import time
import pandas
import numpy as np
import webbrowser
import nibabel as nib
from nilearn import plotting
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
from template.visual import view, run_webserver
from nilearn.masking import compute_epi_mask, apply_mask
from template.templates import get_template, add_string, save_template
from template.futils import make_tmp_folder, make_dir, unzip, get_package_dir
from nipy.algorithms.registration.histogram_registration import HistogramRegistration
from template.plots import make_glassbrain_image, make_anat_image, make_stat_image, get_histogram_data
from mrutils import do_mask, _resample_img, _resample_images_ref, get_standard_brain, get_standard_mask
#from nipy.algorithms.statistics.empirical_pvalue import NormalEmpiricalNull

def run_qa(mr_paths,html_dir,software="FREESURFER",voxdim=[2,2,2],outlier_sds=6,investigator=None):

    # First resample to standard space
    print "Resampling all data to %s using %s standard brain..." %(voxdim,software)
    reference_file = get_standard_brain(software)
    mask_file = get_standard_mask(software)
    images_resamp, reference_resamp = _resample_images_ref(mr_paths,reference_file,voxdim,interpolation="continuous")
    mask = _resample_img(mask_file, affine=np.diag(voxdim))
    mask_bin = compute_epi_mask(mask)
    mask_out = np.zeros(mask_bin.shape)
    mask_out[mask_bin.get_data()==0] = 1
    voxels_out = np.where(mask_out==1)
    total_voxels = np.prod(mask_bin.shape)
    total_voxels_in =  len(np.where(mask_bin.get_data().flatten()==1)[0])
    total_voxels_out = len(np.where(mask_out.flatten()==1)[0])
    mask_out = nib.Nifti1Image(mask_out,affine=mask_bin.get_affine())
      
    # We will save qa values for all in a data frame
    results = pandas.DataFrame(columns=["voxels_in","voxels_out","standard_deviation_resamp","mean_resamp","variance_resamp","median_resamp","mi_score","n_outliers_low_%ssd" %(outlier_sds),"n_outliers_high_%ssd" %(outlier_sds)])

    # We also need to save distributions for the summary page
    all_histograms = []
    image_names = []

    # Calculate a mean image for the entire set
    print "Calculating mean image..."
    mean_image = np.zeros(mask_bin.shape)
    all_masked_data = apply_mask(images_resamp, mask_bin, dtype='f', smoothing_fwhm=None, ensure_finite=True)
    mean_image[mask_bin.get_data()==1] = np.mean(all_masked_data,axis=0)
    mean_image = nib.Nifti1Image(mean_image,affine=mask_bin.get_affine())
    mean_intensity = np.mean(mean_image.get_data()[mask_bin.get_data()==1])
    histogram_data_mean = get_histogram_data(mean_image.get_data()[mask_bin.get_data()==1])
    histogram_mean_counts = ",".join([str(x) for x in histogram_data_mean["counts"]])
    pwd = get_package_dir() 

    images_dir = "%s/img" %(html_dir)
    make_dir(images_dir)
    nib.save(reference_resamp,"%s/standard.nii" %(html_dir))
    nib.save(mask_bin,"%s/mask.nii" %(html_dir))
    nib.save(mask_out,"%s/mask_out.nii" %(html_dir))
    nib.save(mean_image,"%s/mean.nii" %(html_dir))
    make_anat_image("%s/mask.nii" %(html_dir),png_img_file="%s/mask.png" %(html_dir))
    make_anat_image("%s/mask_out.nii" %(html_dir),png_img_file="%s/mask_out.png" %(html_dir))
    make_stat_image("%s/mean.nii" %(html_dir),png_img_file="%s/mean.png" %(html_dir))
    unzip("%s/static/qa_report.zip" %(pwd),html_dir)

    for m in range(0,len(mr_paths)):
      mr = images_resamp[m]
      mr_original = nib.load(mr_paths[m])
      image_name = os.path.split(mr_paths[m])[1]
      print "Generating qa report for %s" %(mr_paths[m])
      
      # Output folder generation
      mr_folder = "%s/%s" %(html_dir,m)
      make_dir(mr_folder)
      mr_images = "%s/img" %(mr_folder)
      make_dir(mr_images)
      masked_in_data = mr.get_data()[mask_bin.get_data()==1]
      masked_out_data = mr.get_data()[mask_out.get_data()==1]
      mr_in_mask,mr_out_mask = make_in_out_mask(mask_bin=mask_bin,mr_folder=mr_folder,masked_in=masked_in_data,masked_out=masked_out_data,img_dir=mr_images)

      # Glass brain, masked, and histogram data
      make_stat_image("%s/masked.nii" %(mr_folder),png_img_file="%s/mr_masked.png" %(mr_images))
      make_glassbrain_image("%s/masked.nii" %(mr_folder),png_img_file="%s/glassbrain.png" %(mr_images))
      metrics = central_tendency(masked_in_data)

      # Header metrics
      mr_metrics = header_metrics(mr_original)
      histogram_data_in = get_histogram_data(masked_in_data)
      histogram_data_out = get_histogram_data(masked_out_data)
      #plot_histogram(masked_in_data,remove_zero=True,title="Voxels inside mask",png_img_file="%s/voxels_in_hist.png" %(mr_images))
      #plot_histogram(masked_out_data,remove_zero=True,title="Voxels outside of mask",png_img_file="%s/voxels_out_hist.png" %(mr_images))

      # Counting voxels (should eventually be in/out brain ratios)
      count_in,count_out = count_voxels(masked_in=masked_in_data,masked_out=masked_out_data)
      high_out,low_out = outliers(masked_in_data,n_std=outlier_sds)

      # Mutual information score against average image
      mi_score = mutual_information_against_standard(mr,mean_image)
          
      # euler characteristics

      # smoothness

      # estimate thresholded or not

      # Add everything to table, prepare single page template
      results.loc[m] = [count_in,count_out,metrics["std"],metrics["mean"],metrics["var"],metrics["med"],mi_score,low_out,high_out]
      template = get_template("qa_single_statmap")

      # Things to fill into individual template
      if m != 0: last_page = m-1;
      else: last_page = len(mr_paths)-1;     
      if m != len(mr_paths)-1: next_page = m+1; 
      else: next_page = 0  
      histogram_in_counts = ",".join([str(x) for x in histogram_data_in["counts"]])
      all_histograms.append(histogram_in_counts)
      image_names.append(image_name)
      histogram_out_counts = ",".join([str(x) for x in histogram_data_out["counts"]]) 
      histogram_bins =  '"%s"' % '","'.join([str(np.round(x,2)) for x in histogram_data_in["bins"]])
      substitutions = {"NUMBER_IMAGES":len(mr_paths),
			"IMAGE_NAME":  image_name,
			"VOXELS_IN_MASK": "{0:.0f}%".format((float(count_in)/float(total_voxels_in)) * 100),
			"VOXELS_OUT_MASK": "{0:.0f}%".format((float(count_out)/float(total_voxels_out)) * 100),
			"TOTAL_VOXELS":total_voxels,
			"MI_SCORE":"%0.2f" % mi_score,
			"MEAN_SCORE":"%0.2f" % metrics["mean"],
			"MEDIAN_SCORE":"%0.2f" % metrics["med"],
			"VARIANCE_SCORE":"%0.2f" % metrics["var"],
			"OUTLIERS_HIGH": high_out,
			"OUTLIERS_LOW":low_out,
			"OUTLIERS_STANDARD_DEVIATION":outlier_sds,
			"STANDARD_DEVIATION_SCORE":"%0.2f" % metrics["std"],
			"STATMAP_HISTOGRAM":histogram_in_counts,
			"MEAN_IMAGE_HISTOGRAM":histogram_mean_counts,
			"NEXT_PAGE":"../%s/%s.html" %(next_page,next_page),
			"LAST_PAGE":"../%s/%s.html" %(last_page,last_page),
                        "OVERLAY_IMAGE":"%s/masked.nii" %(mr_folder)
                      }
      template = add_string(substitutions,template)
      save_template(template,"%s/%s.html" %(mr_folder,m))

    # Individual pages done, now make summary pages, first the histograms
    template = get_template("qa_histograms")
    statmap_histograms = ['<div class="span2 statbox purple" onTablet="span2" onDesktop="span2">\n<div class="boxchart">%s</div><div class="number" style="font-size:30px">%s</div><div class="title">images</div><div class="footer"></div></div>' %(histogram_mean_counts,len(mr_paths))]
    m = 0
    for mean in results["mean_resamp"]:
      if mean >= mean_intensity:    
        statmap_histograms.append('<div class="span2 statbox green" onTablet="span2"\n onDesktop="span2"><div class="boxchart">%s</div><div class="number" style="font-size:30px"><i class="icon-arrow-up"></i></div><div class="title">%s</div><div class="footer"><a href="%s/%s.html"> detail</a></div></div>' %(all_histograms[m],m,m,m))
      else:
        statmap_histograms.append('<div class="span2 statbox red" onTablet="span2"\n onDesktop="span2"><div class="boxchart">%s</div><div class="number" style="font-size:30px"><i class="icon-arrow-down"></i></div><div class="title">%s</div><div class="footer"><a href="%s/%s.html"> detail</a></div></div>' %(all_histograms[m],m,m,m))
      m+=1
    template = add_string({"STATMAP_HISTOGRAMS":"\n".join(statmap_histograms),"NUMBER_IMAGES":len(mr_paths)},template)
    save_template(template,"%s/histograms.html" %(html_dir)) 
    # Summary table page and alerts
    template_summary = get_template("qa_summary_table")
    template_alerts = get_template("qa_alerts")
    statmap_table = []; alerts_passing = []; alerts_outliers = []; count=0;
    for res in results.iterrows():
      # If the image is flagged for an outlier
      if res[1]["n_outliers_low_%ssd" %(outlier_sds)] + res[1]["n_outliers_high_%ssd" %(outlier_sds)] > 0:
        statmap_table.append('<tr><td>%s</td><td class="center">%s</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center"><a class="btn btn-danger" href="%s/%s.html"><i class="icon-flag zoom-in"></i></a></td></tr>' %(image_names[count],count,res[1]["mean_resamp"],res[1]["median_resamp"],res[1]["variance_resamp"],res[1]["standard_deviation_resamp"],res[1]["mi_score"],res[1]["n_outliers_low_%ssd" %(outlier_sds)],res[1]["n_outliers_high_%ssd" %(outlier_sds)],count,count))
        if res[1]["n_outliers_high_%ssd" %(outlier_sds)] > 0: alerts_outliers.append('<div class="task medium"><div class="desc"><div class="title">Outlier High</div><div>Image ID %s has been flagged to have a high outlier</div></div><div class="time"><div class="date">%s</div><div>%s</div></div></div>' %(count,time.strftime("%c"),investigator))
        if res[1]["n_outliers_low_%ssd" %(outlier_sds)] > 0: alerts_outliers.append('<div class="task medium"><div class="desc"><div class="title">Outlier Low</div><div>Image ID %s has been flagged to have a high outlier</div></div><div class="time"><div class="date">%s</div><div>%s</div></div></div>' %(count,time.strftime("%c"),investigator))
      else: 
        statmap_table.append('<tr><td>%s</td><td class="center">%s</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center"><a class="btn btn-success" href="%s/%s.html"><i class="icon-check zoom-in"></i></a></td></tr>' %(image_names[count],count,res[1]["mean_resamp"],res[1]["median_resamp"],res[1]["variance_resamp"],res[1]["standard_deviation_resamp"],res[1]["mi_score"],res[1]["n_outliers_low_%ssd" %(outlier_sds)],res[1]["n_outliers_high_%ssd" %(outlier_sds)],count,count))
        alerts_passing.append('<div class="task low"><div class="desc"><div class="title">%s</div><div>This map has no flags as determined by the standards of only this report.</div></div><div class="time"><div class="date">%s</div><div>%s</div></div></div>' %(image_names[count],time.strftime("%c"),investigator))
      count+=1
    if alerts_outliers: alerts_outliers[-1] = alerts_outliers[-1].replace("task medium","task medium last")
    template_alerts = add_string({"ALERTS_PASSING":"\n".join(alerts_passing),"ALERTS_OUTLIERS":"\n".join(alerts_outliers),"NUMBER_IMAGES":len(mr_paths),"OUTLIERS_STANDARD_DEVIATIONS":outlier_sds},template_alerts)
    template_summary = add_string({"STATMAP_TABLE":"\n".join(statmap_table),"NUMBER_IMAGES":len(mr_paths),"OUTLIERS_STANDARD_DEVIATIONS":outlier_sds},template_summary)
    save_template(template_summary,"%s/summary.html" %(html_dir)) 
    save_template(template_alerts,"%s/alerts.html" %(html_dir)) 
    
    # Finally, save the index
    index_template = get_template("qa_index")
    image_gallery = ['<div id="image-%s" class="masonry-thumb"><a style="background:url(%s/img/glassbrain.png) width=200px" title="%s" href="%s/%s.html"><img class="grayscale" src="%s/img/glassbrain.png" alt="%s"></a></div>' %(m,m,image_names[m],m,m,m,image_names[m]) for m in range(0,len(mr_paths)) ]
    substitutions = {"MEAN_IMAGE_HISTOGRAM":histogram_mean_counts,
		     "GLASSBRAIN_GALLERY":"\n".join(image_gallery),
                     "NUMBER_OUTLIERS":len(alerts_outliers),
                     "NUMBER_THRESH":0,
                     "NUMBER_IMAGES":len(mr_paths)
                    }
    index_template = add_string(substitutions,index_template)
    save_template(index_template,"%s/index.html" %(html_dir))

    # Save results to file
    results.to_csv("%s/allMetrics.tsv" %(html_dir),sep="\t")
    os.chdir(html_dir)
    run_webserver(PORT=8091)

'''Metrics:
Extract metrics from the header
'''
def header_metrics(image):
  mr_affine = image.get_affine()
  mr_shape = image.shape
  header = image.get_header()
  return {"shape":mr_shape,"affine":mr_affine,"header":header}

'''Central tendency:
standard measures of central tendency and variance
'''
def central_tendency(data):
  mr_mean = data.mean()
  mr_var = data.var()
  mr_std = data.std()
  mr_med = np.median(data)
  return {"std":mr_std,"var":mr_var,"mean":mr_mean,"med":mr_med}


'''Normality across nonzero
normality of the distribution across non-zero voxels
'''
#def normality_across_nonzero(data,out_png=None):
#  x = np.c_[data]
#  enn = NormalEmpiricalNull(x)
#  enn.threshold(verbose=True)

'''Outliers
outliers (e.g., more than ~6 SD from the mean, maybe less depending on the action)
'''
def outliers(masked_data,n_std=6):
  mean = masked_data.mean()
  std = masked_data.std()
  six_dev_up = mean + n_std * std
  six_dev_down = mean - n_std*std
  high_outliers = len(np.where(masked_data>=six_dev_up)[0])
  low_outliers = len(np.where(masked_data<=six_dev_down)[0])
  return high_outliers,low_outliers

'''Mutual Information Against Standard
# mutual information against some mean map that is representative of an # expectation [really low --> something is funky]
'''
def mutual_information_against_standard(mr,mean_image):
  mi = HistogramRegistration(mean_image, mr, similarity='nmi')  
  T = mi.optimize("affine")
  return mi.explore(T)[0][0]


'''Estimate thresholded
counting zeros / nans to estimate if map has been thresholded
'''
#def estimate_thresholded():
#  "WRITE ME" 

'''make in out mask
Generate masked image, return two images: voxels in mask, and voxels outside
'''
def make_in_out_mask(mask_bin,mr_folder,masked_in,masked_out,img_dir):
  mr_in_mask = np.zeros(mask_bin.shape)
  mr_out_mask = np.zeros(mask_bin.shape)
  mr_out_mask[mask_bin.get_data()==0] = masked_out
  mr_out_mask = nib.Nifti1Image(mr_out_mask,affine=mask_bin.get_affine(),header=mask_bin.get_header())
  mr_in_mask[mask_bin.get_data()!=0] = masked_in
  mr_in_mask = nib.Nifti1Image(mr_in_mask,affine=mask_bin.get_affine(),header=mask_bin.get_header())
  nib.save(mr_in_mask,"%s/masked.nii" %(mr_folder))
  nib.save(mr_out_mask,"%s/masked_out.nii" %(mr_folder))
  make_anat_image("%s/masked.nii" %(mr_folder),png_img_file="%s/masked.png" %(img_dir))
  make_anat_image("%s/masked_out.nii" %(mr_folder),png_img_file="%s/masked_out.png" %(img_dir))
  return mr_in_mask,mr_out_mask

'''Count voxels in and outside the mask
possibly need to change this to get "close to" zero
'''
def count_voxels(masked_in,masked_out):
  # Here we are assuming a value of 0 == not in mask
  count_in = len(masked_in[masked_in!=0])
  count_out = len(masked_out[masked_out!=0])
  return count_in,count_out

