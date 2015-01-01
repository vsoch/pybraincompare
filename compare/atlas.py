import nibabel
import pandas
import numpy
import os
import re
import cairo
from xml.dom import minidom
from nilearn import plotting
from scipy.spatial.distance import pdist, squareform
from skimage.segmentation import felzenszwalb
from skimage.segmentation import mark_boundaries, find_boundaries
from skimage.util import img_as_float
import pylab as pl
from futils import make_tmp_folder
from mrutils import percent_to_float

class region:
  def __init__(self,label,index,x,y,z):
    self.label = label
    self.index = index
    self.x = x
    self.y = y
    self.z = z

# Atlas object to hold a nifti object and xml labels

class atlas:
  def __init__(self,atlas_xml,atlas_file,views=["axial","sagittal","coronal"]):
    self.file = atlas_file
    self.xml = atlas_xml
    self.mr = nibabel.load(atlas_file)
    self.labels = self.read_xml(atlas_xml)
    self.svg, self.paths, self.svg_file = self.make_svg(views)

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
  
  '''Generate static svg of atlas (cannot manipulate in d3)'''
  def get_static_svg(self):
    svg_data = []
    with make_tmp_folder() as temp_dir:
      output_file='%s/atlas.svg' %(temp_dir)
      plotting.plot_roi(self.mr,annotate=False,draw_cross=False,cmap="nipy_spectral",black_bg=False, output_file=output_file)
      svg_file = open(output_file,'r')
      svg_data = svg_file.readlines()
      svg_file.close()
    return svg_data[4:]

  '''Generate path-based svg of atlas (paths we can manipulate in d3)'''
  def make_svg(self,views):
    # We will save complete svg (for file), partial (for embedding), and paths
    svg_data = dict(); svg_data_partial = dict(); svg_data_file = dict();
    if isinstance(views,str): views = [views]
    views = [v.lower() for v in views]
    self.views = views
    mr = self.mr.get_data()      
    middles = [numpy.round(x/2) for x in self.mr.get_shape()]         
    with make_tmp_folder() as temp_dir:
      
      # Get all unique regions (may not be present in every slice)
      regions = [ x for x in numpy.unique(mr) if x != 0]

      # Generate unique color for each region (can be changed later)
      colors = [numpy.round(numpy.random.random_sample(3),1) for x in range(0,len(regions))]
        
      # Generate an axial, sagittal, coronal view
      slices = dict()
      for v in views:
        # Generate each of the views
        if v == "axial": slices[v] = numpy.rot90(mr[:,:,middles[0]],2)
        elif v == "sagittal" : slices[v] = numpy.rot90(mr[middles[1],:,:],2)
        elif v == "coronal" : slices[v] = numpy.rot90(mr[:,middles[2],:],2)

        # For each region in the view, but not 0
        regions = [ x for x in numpy.unique(slices[v]) if x != 0]

        # Write svg to temporary file
        output_file = '%s/%s_atlas.svg' %(temp_dir,v)
        fo = file(output_file, 'wb')

        # Set up the "context" - what cairo calls a canvas
        width, height  = numpy.shape(slices[v])
        surface = cairo.SVGSurface (fo, width*3, height*3)
        ctx = cairo.Context (surface)
        ctx.scale(3.,3.)    

        # 90 degree rotation matrix
        rotation_matrix = cairo.Matrix.init_rotate(numpy.pi/2)
    
        for rr in range(0,len(regions)):
          index_value = regions[rr]
          filtered = numpy.zeros(numpy.shape(slices[v]))
          filtered[slices[v] == regions[rr]] = 1
          region = img_as_float(find_boundaries(filtered)) # We aren't using Canny anymore...

          ctx.set_source_rgb (float(colors[index_value-1][0]), float(colors[index_value-1][1]), float(colors[index_value-1][2])) # Solid color

          # Segment!
          segments_fz = felzenszwalb(region, scale=100, sigma=0.1, min_size=10)

          # For each cluster in the region, skipping value of 0
          for c in range(1,len(numpy.unique(segments_fz))):
            cluster = numpy.zeros(numpy.shape(region))
            cluster[segments_fz==c] = 1
            # Create distance matrix for points
            x,y = numpy.where(cluster==1)
            points = [[x[i],y[i]] for i in range(0,len(x))]
            disty = squareform(pdist(points, 'euclidean'))
            # This keeps track of which we have already visited
            visited = []; row = 0; current = points[row]
            visited.append(row)
    
            # We need to remember the first point, for the last one
            fp = current

            while len(visited) != len(points):
              thisx = current[0]
              thisy = current[1]
              ctx.move_to(thisx, thisy)
              # Find closest point, only include columns we have not visited
              distances = disty[row,:]
              distance_lookup = dict()
              # We need to preserve indices but still eliminate visited 
              for j in range(0,len(distances)):
                if j not in visited: distance_lookup[j] = distances[j]
              # Get key minimum distance
              row = min(distance_lookup, key=distance_lookup.get)
              next = points[row]
              nextx = next[0]
              nexty = next[1]
              # If the distance is more than N pixels, close the path
              # This resolves some of the rough edges too
              if min(distance_lookup) > 70:
                ctx.line_to(fp[0],fp[1])
                #cp = [(current[0]+fp[0])/2,(current[1]+fp[1])/2] 
                #ctx.curve_to(fp[0],fp[1],cp[0],cp[1],cp[0],cp[1])
                ctx.set_line_width(1)
                ctx.close_path()
                fp = next
              else:    
                #cp = [(current[0]+nextx)/2,(current[1]+nexty)/2] 
                #ctx.curve_to(nextx,nexty,cp[0],cp[1],cp[0],cp[1])
                ctx.line_to(nextx, nexty)
                # Set next point to be current
              visited.append(row)
              current = next
    
            # Go back to the first point
            ctx.move_to(current[0],current[1])
            #cp = [(current[0]+fp[0])/2,(current[1]+fp[1])/2] 
            #ctx.curve_to(fp[0],fp[1],cp[0],cp[1],cp[0],cp[1])
            ctx.line_to(fp[0],fp[1])
            # Close the path
            ctx.set_line_width (1)
            ctx.stroke()
    
        # Finish the surface
        surface.finish()
        fo.close()

        # Now grab the file, set attributes 
        # Give group name based on atlas, region id based on matching color
        dom = minidom.parse(output_file)
        for group in dom.getElementsByTagName("g"):
          group.setAttribute("id",os.path.split(self.file)[-1])
          group.setAttribute("class",v)
        expression = re.compile("stroke:rgb")
        # Add class to svg - important so can manipulate in d3
        dom.getElementsByTagName("svg")[0].setAttribute("class",v)
        for path in dom.getElementsByTagName("path"):
          style = path.getAttribute("style")
          color = [x for x in style.split(";") if expression.search(x)][0]
          style = style.replace("none",color.replace("stroke:",""))
          color = [percent_to_float(x) for x in color.replace("stroke:rgb(","").replace(")","").split(",")]
          region_index = [x for x in range(0,len(colors)) if numpy.equal(colors[x],color).all()][0]+1
          region_label = self.labels[str(region_index)].label
          path.setAttribute("id",region_label)
          path.setAttribute("style",style)
        svg_data_file[v] = dom.toxml()
        svg_data[v] = dom.toxml().replace("<?xml version=\"1.0\" ?>","") # get rid of just xml tag
        svg_data_partial[v] = "/n".join(dom.toxml().split("\n")[1:-1])
    return svg_data, svg_data_partial, svg_data_file

  '''Save svg data to file'''
  def save_svg(self,output_folder,views=None):
    if not views: views = self.views
    if not output_folder:
      print "Please specify an output directory"
    else:
      atlas_name = os.path.split(self.file)[-1].replace("[.]","-")
      for v in views:
        filey = open( "%s/%s-%s.svg" %(output_folder,atlas_name,v) ,"wb")
        filey.writelines(self.svg_file[v])
        filey.close()

  '''Internal function to change color of svg xml'''
  def set_color(self,new_color):
    new_svg_xml = dict()
    for tag, svg in self.svg_file.iteritems():
      dom = minidom.parseString(svg)
      for path in dom.getElementsByTagName("path"):
        expression = re.compile("stroke:rgb")
        #TODO: turn this into a function
        style = path.getAttribute("style")
        color = [x for x in style.split(";") if expression.search(x)][0]
        style = style.replace(color,"stroke:%s" %(new_color))
        path.setAttribute("style",style)
      new_svg_xml[tag] = dom.toxml()
      self.svg[tag] = dom.toxml().replace("<?xml version=\"1.0\" ?>","")
      self.paths[tag] = "/n".join(dom.toxml().split("\n")[1:-1])
    self.svg_file = new_svg_xml
