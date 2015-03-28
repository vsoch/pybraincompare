'''
colors.py: part of pybraincompare package
Color stuffs

'''

import random

'''Generate N random colors'''
def random_colors(N):
  colors = []
  for x in range(0,N):
    r = lambda: random.randint(0,255)
    colors.append('#%02X%02X%02X' % (r(),r(),r()))
  return colors


'''Get colors that I like'''
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


'''Colors for Peterson ROI labels'''
def peterson_roi_labels(colors=True):
  color_labels = ["Default","Second-Dorsal-Attention","Ventral-Attention-Language","Second-Visual","Frontal-Parietal","Somatomotor","none","Parietal-Episodic-Retrieval","Parieto-Occipital","Cingulo-opercular","Salience","Frontal-Parietal-Other","First-Dorsal-Attention","First-Visual-V1+","Subcortical"]
  colors = ["#ff2700","#d6add6","#007d7d","#393FAC","#FFFB00","#00ffff","94CD54","#CC0066","#003eff","#fbfbda","#822082","#000000","#c46b8b","#00f700","#94cd54","#CC0066"]
  if not colors: return color_labels
  else: return [colors,color_labels]


