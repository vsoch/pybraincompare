import nibabel
import pandas
import numpy
import os
from xml.dom import minidom

class region:
  def __init__(self,label,index,x,y,z):
    self.label = label
    self.index = index
    self.x = x
    self.y = y
    self.z = z

# Atlas object to hold a nifti object and xml labels

class atlas:
  def __init__(self,atlas_xml,atlas_file):
    self.file = atlas_file
    self.xml = atlas_xml
    self.mr = nibabel.load(atlas_file)
    self.labels = self.read_xml(atlas_xml)

  def read_xml(self,atlas_xml):
    dom = minidom.parse(atlas_xml)
    atlases = []
    image_file = os.path.split(os.path.splitext(self.file)[0])[-1]
    for atlas in dom.getElementsByTagName("summaryimagefile"):
      atlases.append(str(os.path.split(atlas.lastChild.nodeValue)[-1]))
    if image_file in atlases:
      labels = {}
      # A value of 0 indicates no label in the image
      labels["0"] = region("No Label",0,0,0,0)
      for lab in dom.getElementsByTagName("label"):
        # Caution - the index is 1 less than image value
        labels[str(int(lab.getAttribute("index"))+1)] = region(lab.lastChild.nodeValue, (int(lab.getAttribute("index"))+1), lab.getAttribute("x"), lab.getAttribute("y"), lab.getAttribute("z"))
      return labels    
    else:
      print "ERROR: xml file atlas name does not match given atlas name!"
