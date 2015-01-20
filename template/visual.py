# Functions for visualization parameters
from template.futils import make_tmp_folder
from nilearn.plotting import plot_glass_brain
import matplotlib.pyplot as plt
import webbrowser

'''Display code in temporary browser!'''
def view(html_snippet):
  with make_tmp_folder() as tmp_dir:  
    # Write to temporary file
    tmp_file = "%s/pycompare.html" %(tmp_dir)
    html_file = open(tmp_file,'wb')
    html_file.writelines(html_snippet)
    html_file.close()
    url = 'file://%s' %(tmp_file)
    webbrowser.open_new_tab(url)
    raw_input("Press Enter to finish...")

def get_colors(N,color_format="decimal"):
  # color scale chosen manually that I like :)
  colors = [[122,197,205],[71,60,139],[255,99,71],[118,238,0],[100,149,237],[255,127,36],[139,0,0],[255,48,48],[34,139,34],[0,206,209],[160,32,240],[238,201,0],[89,89,89],[238,18,137],[205,179,139],[255,0,0]]
  if color_format == "hex":
    colors = ["#7AC5CD","#473C8B","#FF6347","#76EE00","#6495ED","#FF7F24","#8B0000","#FF3030","#228B22","#00CED1","#A020F0","#EEC900","#595959","#EE1289","#CDB38B","#FF0000"]
  elif color_format == "decimal":
    colors = [[round(x/255.0,1) for x in c] for c in colors ]
  else:   
    print "%s is not a valid format." %(color_format)
    return

  if N <= len(colors):  
    colors = colors[0:N]
    return colors
  else:
    print "Current colorscale only has %s colors! Add more!" %(len(colors))

"""Make glassbrain image, optional save image to png file (not vector)"""
def make_glassbrain_image(nifti_file,png_img_file=None):
    nifti_file = str(nifti_file)
    glass_brain = plot_glass_brain(nifti_file)
    if png_img_file:    
      glass_brain.savefig(png_img_file)
    plt.close()
    return glass_brain

