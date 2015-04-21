'''
webreport.py: part of pybraincompare package
Functions to generate reports using qa tools

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
from pybraincompare.template.visual import view, run_webserver
from nilearn.masking import compute_epi_mask, apply_mask
from pybraincompare.template.templates import get_template, add_string, save_template
from pybraincompare.template.futils import make_tmp_folder, make_dir, unzip, get_package_dir
from pybraincompare.report.static import make_glassbrain_image, make_anat_image, make_stat_image
from pybraincompare.report.histogram import get_histogram_data
from qa import header_metrics, central_tendency, outliers, get_percent_nonzero, count_voxels, is_thresholded
from pybraincompare.compare.mrutils import do_mask, resample_images_ref, get_standard_brain, get_standard_mask, make_in_out_mask
from nilearn.image import resample_img

'''run_qa: a tool to generate an interactive qa report for statistical maps

mr_paths: a list of paths to brain statistical maps that can be read with nibabel [REQUIRED]
software: currently only freesurfer is supporte [default:FREESURFER]
voxdim: a list of x,y,z dimensions to resample data when normalizing [default [2,2,2]]
outlier_sds: the number of standard deviations from the mean to define an outlier [default:6]
investigator: the name (string) of an investigator to add to alerts summary page [defauflt:None]
nonzero_thresh: images with # of nonzero voxels in brain mask < this value will be flagged as thresholded [default:0.25] 
calculate_mean_image: Default True, should be set to False for larger datasets where memory is an issue
view: view the web report in a browser at the end [default:True]

'''
def run_qa(mr_paths,html_dir,software="FSL",voxdim=[2,2,2],outlier_sds=6,investigator="brainman",
           nonzero_thresh=0.25,calculate_mean_image=True,view=True):

    # First resample to standard space
    print "Resampling all data to %s using %s standard brain..." %(voxdim,software)
    reference_file = get_standard_brain(software)
    mask_file = get_standard_mask(software)
    images_resamp, reference_resamp = resample_images_ref(mr_paths,reference_file,resample_dim=voxdim,interpolation="continuous")
    mask = resample_img(mask_file, target_affine=np.diag(voxdim))
    mask_bin = compute_epi_mask(mask)
    mask_out = np.zeros(mask_bin.shape)
    mask_out[mask_bin.get_data()==0] = 1
    voxels_out = np.where(mask_out==1)
    total_voxels = np.prod(mask_bin.shape)
    total_voxels_in =  len(np.where(mask_bin.get_data().flatten()==1)[0])
    total_voxels_out = len(np.where(mask_out.flatten()==1)[0])
    mask_out = nib.Nifti1Image(mask_out,affine=mask_bin.get_affine())
      
    # We will save qa values for all in a data frame
    results = pandas.DataFrame(columns=["voxels_in","voxels_out","standard_deviation_resamp","mean_resamp","variance_resamp","median_resamp","n_outliers_low_%ssd" %(outlier_sds),"n_outliers_high_%ssd" %(outlier_sds),"nonzero_percent_voxels_in_mask","threshold_flag"])

    # We also need to save distributions for the summary page
    all_histograms = []
    image_names = []

    # Set up directories
    pwd = get_package_dir() 
    images_dir = "%s/img" %(html_dir)
    make_dir(images_dir)
   

    # Calculate a mean image for the entire set
    if calculate_mean_image == True:
        print "Calculating mean image..."
        all_masked_data = apply_mask(images_resamp, mask_bin, dtype='f', smoothing_fwhm=None, ensure_finite=True)
        mean_image = np.zeros(mask_bin.shape)
        mean_image[mask_bin.get_data()==1] = np.mean(all_masked_data,axis=0)
        mean_image = nib.Nifti1Image(mean_image,affine=mask_bin.get_affine())
        mean_intensity = np.mean(mean_image.get_data()[mask_bin.get_data()==1])
        histogram_data_mean = get_histogram_data(mean_image.get_data()[mask_bin.get_data()==1])
        histogram_mean_counts = ",".join([str(x) for x in histogram_data_mean["counts"]])
        nib.save(mean_image,"%s/mean.nii" %(html_dir))
        make_stat_image("%s/mean.nii" %(html_dir),png_img_file="%s/mean.png" %(html_dir))    

    nib.save(reference_resamp,"%s/standard.nii" %(html_dir))
    nib.save(mask_bin,"%s/mask.nii" %(html_dir))
    nib.save(mask_out,"%s/mask_out.nii" %(html_dir))
    make_anat_image("%s/mask.nii" %(html_dir),png_img_file="%s/mask.png" %(html_dir))
    make_anat_image("%s/mask_out.nii" %(html_dir),png_img_file="%s/mask_out.png" %(html_dir))
    
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

      # Counting voxels (should eventually be in/out brain ratios)
      count_in,count_out = count_voxels(masked_in=masked_in_data,masked_out=masked_out_data)
      high_out,low_out = outliers(masked_in_data,n_std=outlier_sds)
          
      # euler characteristics
      # smoothness

      # estimate thresholded or not. If the original image is the same shape as the mask, use it
      if mr_original.shape == mask.shape:
        threshold_flag,percent_nonzero = is_thresholded(mr_original,mask,threshold=nonzero_thresh)
      else: # this will return biased high values because we have resampled with this standard!
        threshold_flag,percent_nonzero = is_thresholded(mr,mask,threshold=nonzero_thresh)
      
      # Add everything to table, prepare single page template
      results.loc[m] = [count_in,count_out,metrics["std"],metrics["mean"],metrics["var"],metrics["med"],low_out,high_out,percent_nonzero,threshold_flag]

      if calculate_mean_image == True:
          template = get_template("qa_single_statmap_mean")
      else:
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
			"NONZERO_VOXELS": "%0.3f" % (percent_nonzero),
			"THRESHOLD_FLAG": "%s" % (threshold_flag),
			"NONZERO_THRESH": "%s" % (nonzero_thresh),
			"TOTAL_VOXELS":total_voxels,
			"MEAN_SCORE":"%0.2f" % metrics["mean"],
			"MEDIAN_SCORE":"%0.2f" % metrics["med"],
			"VARIANCE_SCORE":"%0.2f" % metrics["var"],
			"OUTLIERS_HIGH": high_out,
			"OUTLIERS_LOW":low_out,
			"OUTLIERS_STANDARD_DEVIATION":outlier_sds,
			"STANDARD_DEVIATION_SCORE":"%0.2f" % metrics["std"],
			"STATMAP_HISTOGRAM":histogram_in_counts,
			"NEXT_PAGE":"../%s/%s.html" %(next_page,next_page),
			"LAST_PAGE":"../%s/%s.html" %(last_page,last_page),
                        "OVERLAY_IMAGE":"%s/masked.nii" %(mr_folder),
                        "INVESTIGATOR":investigator
                      }
      template = add_string(substitutions,template)
      if calculate_mean_image == True:
          template = add_string({"MEAN_IMAGE_HISTOGRAM":histogram_mean_counts},template)
      save_template(template,"%s/%s.html" %(mr_folder,m))

    # Individual pages done, now make summary pages, first the histograms
    template = get_template("qa_histograms")
    if calculate_mean_image == True:
        statmap_histograms = ['<div class="span2 statbox purple" onTablet="span2" onDesktop="span2">\n<div class="boxchart">%s</div><div class="number" style="font-size:30px">%s</div><div class="title">images</div><div class="footer"></div></div>' %(histogram_mean_counts,len(mr_paths))]
    else:
        statmap_histograms = [] 
       
    m = 0
    for mean in results["mean_resamp"]:
      if calculate_mean_image == True:
          if mean >= mean_intensity:    
              statmap_histograms.append('<div class="span2 statbox blue" onTablet="span2"\n onDesktop="span2"><div class="boxchart">%s</div><div class="number" style="font-size:30px"><i class="icon-arrow-up"></i></div><div class="title">%s</div><div class="footer"><a href="%s/%s.html"> detail</a></div></div>' %(all_histograms[m],m,m,m))
          else:
              statmap_histograms.append('<div class="span2 statbox red" onTablet="span2"\n onDesktop="span2"><div class="boxchart">%s</div><div class="number" style="font-size:30px"><i class="icon-arrow-down"></i></div><div class="title">%s</div><div class="footer"><a href="%s/%s.html"> detail</a></div></div>' %(all_histograms[m],m,m,m))
      else:
          statmap_histograms.append('<div class="span2 statbox red" onTablet="span2"\n onDesktop="span2"><div class="boxchart">%s</div><div class="number" style="font-size:30px"></div><div class="title">%s</div><div class="footer"><a href="%s/%s.html"> detail</a></div></div>' %(all_histograms[m],m,m,m))
      m+=1
    template = add_string({"STATMAP_HISTOGRAMS":"\n".join(statmap_histograms),
                           "NUMBER_IMAGES":len(mr_paths),
                           "INVESTIGATOR":investigator},template)
    save_template(template,"%s/histograms.html" %(html_dir)) 

    # Summary table page and alerts
    template_summary = get_template("qa_summary_table")
    template_alerts = get_template("qa_alerts")
    statmap_table = []; alerts_passing = []; alerts_outliers = []; alerts_thresh = []; count=0;
    for res in results.iterrows():

      # SUMMARY ITEMS ----

      # If the image has too many zeros:
      if res[1]["threshold_flag"] == True:
        alerts_thresh.append('<div class="task high"><div class="desc"><div class="title">Thresholded Map</div><div>Image ID %s has been flagged as being thresholded! Nonzero voxels in mask: %s.</div></div><div class="time"><div class="date">%s</div></div></div>' %(count,res[1]["nonzero_percent_voxels_in_mask"],time.strftime("%c")))

      # If the image has outliers or is thresholded:
      total_outliers = res[1]["n_outliers_low_%ssd" %(outlier_sds)] + res[1]["n_outliers_high_%ssd" %(outlier_sds)]
      flagged = (total_outliers > 0) | res[1]["threshold_flag"]

      if flagged == True:
        statmap_table.append('<tr><td>%s</td><td class="center">%s</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center"><a class="btn btn-danger" href="%s/%s.html"><i class="icon-flag zoom-in"></i></a></td></tr>' %(image_names[count],count,res[1]["mean_resamp"],res[1]["median_resamp"],res[1]["variance_resamp"],res[1]["standard_deviation_resamp"],res[1]["n_outliers_low_%ssd" %(outlier_sds)],res[1]["n_outliers_high_%ssd" %(outlier_sds)],count,count))
        if res[1]["n_outliers_high_%ssd" %(outlier_sds)] > 0: 
          alerts_outliers.append('<div class="task medium"><div class="desc"><div class="title">Outlier High</div><div>Image ID %s has been flagged to have a high outlier</div></div><div class="time"><div class="date">%s</div><div></div></div></div>' %(count,time.strftime("%c")))
        if res[1]["n_outliers_low_%ssd" %(outlier_sds)] > 0: 
          alerts_outliers.append('<div class="task medium"><div class="desc"><div class="title">Outlier Low</div><div>Image ID %s has been flagged to have a high outlier</div></div><div class="time"><div class="date">%s</div><div></div></div></div>' %(count,time.strftime("%c")))

      # Image is passing!
      else: 
        statmap_table.append('<tr><td>%s</td><td class="center">%s</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center">%0.2f</td><td class="center"><a class="btn btn-success" href="%s/%s.html"><i class="icon-check zoom-in"></i></a></td></tr>' %(image_names[count],count,res[1]["mean_resamp"],res[1]["median_resamp"],res[1]["variance_resamp"],res[1]["standard_deviation_resamp"],res[1]["n_outliers_low_%ssd" %(outlier_sds)],res[1]["n_outliers_high_%ssd" %(outlier_sds)],count,count))
        alerts_passing.append('<div class="task low"><div class="desc"><div class="title">%s</div><div>This map has no flags as determined by the standards of only this report.</div></div><div class="time"><div class="date">%s</div><div></div></div></div>' %(image_names[count],time.strftime("%c")))
      count+=1

    # ALERTS ITEMS ----

    # In the case of zero of any of the above
    if len(alerts_thresh) == 0: 
      alerts_thresh = ['<div class="task high last"><div class="desc"><div class="title">No Thresholded Maps</div><div>No images have been flagged as thresholded [percent nonzero voxels in mask <= %s]</div></div><div class="time"><div class="date">%s</div></div></div>' %(nonzero_thresh,time.strftime("%c"))]
      number_thresh = 0
    else:  
      alerts_thresh[-1] = alerts_thresh[-1].replace("task high","task high last")
      number_thresh = len(alerts_thresh)
    
    if len(alerts_outliers) == 0: 
      alerts_outliers = ['<div class="task medium last"><div class="desc"><div class="title">No Outliers</div><div>No images have been flagged for outliers %s standard deviations in either direction.</div></div><div class="time"><div class="date">%s</div></div></div>' %(outlier_sds,time.strftime("%c"))]
      number_outliers = 0
    else:     
      alerts_outliers[-1] = alerts_outliers[-1].replace("task medium","task medium last")
      number_outliers = len(alerts_outliers)
    
    if len(alerts_passing) == 0: 
      alerts_passing = ['<div class="task low last"><div class="desc"><div class="title">No Passing!</div><div>No images are passing! What did you do?!</div></div><div class="time"><div class="date">%s</div></div></div>' %(time.strftime("%c"))]
    
    # Alerts and summary template
    template_alerts = add_string({"ALERTS_PASSING":"\n".join(alerts_passing),
                                  "ALERTS_OUTLIERS":"\n".join(alerts_outliers),
                                  "NUMBER_IMAGES":len(mr_paths),
                                  "OUTLIERS_STANDARD_DEVIATIONS":outlier_sds,
                                  "ALERTS_THRESH":"\n".join(alerts_thresh),
                                  "INVESTIGATOR":investigator},template_alerts)
    template_summary = add_string({"STATMAP_TABLE":"\n".join(statmap_table),
                                   "NUMBER_IMAGES":len(mr_paths),
                                   "OUTLIERS_STANDARD_DEVIATIONS":outlier_sds,
                                   "INVESTIGATOR":investigator},template_summary)
    save_template(template_summary,"%s/summary.html" %(html_dir)) 
    save_template(template_alerts,"%s/alerts.html" %(html_dir)) 
    
    # Finally, save the index
    index_template = get_template("qa_index")
    image_gallery = ['<div id="image-%s" class="masonry-thumb"><a style="background:url(%s/img/glassbrain.png) width=200px" title="%s" href="%s/%s.html"><img class="grayscale" src="%s/img/glassbrain.png" alt="%s"></a></div>' %(m,m,image_names[m],m,m,m,image_names[m]) for m in range(0,len(mr_paths)) ]
    substitutions = {"GLASSBRAIN_GALLERY":"\n".join(image_gallery),
                     "NUMBER_OUTLIERS":number_outliers,
                     "NUMBER_THRESH":number_thresh,
                     "NUMBER_IMAGES":len(mr_paths),
                     "INVESTIGATOR":investigator
                    }
    index_template = add_string(substitutions,index_template)
    if calculate_mean_image == True:
        index_template = add_string({"MEAN_IMAGE_HISTOGRAM":histogram_mean_counts},index_template)
    save_template(index_template,"%s/index.html" %(html_dir))

    # Save results to file
    results.to_csv("%s/allMetrics.tsv" %(html_dir),sep="\t")
    if view==True:
        os.chdir(html_dir)
        run_webserver(PORT=8091)
