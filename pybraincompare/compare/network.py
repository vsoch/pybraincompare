'''
network.py: part of pybraincompare package
Functions for visualization of functional MRI

'''
from pybraincompare.template.templates import get_template, add_string
from pybraincompare.report.colors import random_colors
from pybraincompare.template.futils import get_name
import nibabel
import pandas
import numpy
import json
import os

# Connectogram data visualization
'''connectogram: Generate a d3 connectogram for a functionary connectivity matrix.
matrix_file: a tab separated correlation matrix
groups: a list of connection groups, whatever names you want
threshold: a 99% (.99) threhsold means we include the top 1% of negative and positive values
'''
def connectogram(matrix_file,groups,threshold,network_names=None):
   conn_df = pandas.read_csv(matrix_file,sep="\t")
   if conn_df.shape[0] != conn_df.shape[1]:
     print "Matrix is size [%s,%s], please check file formatting!" %(conn_df.shape[0],conn_df.shape[1])
     return
  
   if not network_names:
     network_names = groups

   # Fill NaN with 0 in matrix
   conn_df = conn_df.fillna(0)
   pos_df = conn_df.copy()
   neg_df = conn_df.copy()
   pos_df[pos_df<0] = 0
   neg_df[neg_df>0] = 0
   pos_df = pos_df.fillna(0)
   neg_df = neg_df.fillna(0)

   # Try getting quantiles for top and bottom
   qpos = numpy.percentile(pos_df,threshold*100)
   qneg = numpy.percentile(neg_df,threshold*100)

   pos_df[pos_df < qpos] = 0
   neg_df[neg_df > (-1*qneg)] = 0
   pos_df = pos_df.fillna(0)
   neg_df = neg_df.fillna(0)
   thresh_df = pos_df + neg_df
  
   # Get colors
   unique_networks = numpy.unique(network_names)
   colors = random_colors(len(unique_networks))
   network_colors = dict()
   for network in unique_networks: network_colors[network] = colors.pop(0)

   # Network node labels
   labels = list(thresh_df.columns)

   # For each, we will output a json object with our variables of interest
   myjson = []  
   c = 0
   for row in thresh_df.iterrows():
     connections = numpy.where(row[1] != 0)   
     network = network_names[c]
     if len(connections[0]) > 0: 
       connection_names = list(thresh_df.columns[connections]) 
       connection_groups = [groups[x] for x in connections[0]]      
       connection_labels = ["%s.%s" %(connection_groups[i],connection_names[i]) for i in range(0,len(connections[0]))]       
       connection_labels_string = '","'.join([str(x) for x in connection_labels])
       connection_values = row[1][connections[0]]
       connection_values_string = "|".join([str(x) for x in connection_values])
       # If we aren't at the last row       
       if c+1 != thresh_df.shape[0]:  
         myjson.append('{"name":"%s.%s","strength":"%s","x":99,"y":99,"z":99,"image":"#","order":%s,"color":"%s","network":"%s","connections":["%s"]},' %(groups[c],labels[c],connection_values_string,labels[c],network_colors[network],network,connection_labels_string))
       else:
         myjson.append('{"name":"%s.%s","strength":"%s","x":99,"y":99,"z":99,"image":"#","order":%s,"color":"%s","network":"%s","connections":["%s"]}' %(groups[c],labels[c],connection_values_string,labels[c],network_colors[network],network,connection_labels_string))
     # If there are no connections
     else:
       if c+1 != thresh_df.shape[0]:  
         myjson.append('{"name":"%s.%s","x":99,"y":99,"z":99,"image":"#","order":%s,"color":"%s","network":"%s"},' %(groups[c],labels[c],labels[c],network_colors[network],network))
       else:
         myjson.append('{"name":"%s.%s","x":99,"y":99,"z":99,"image":"#","order":%s,"color":"%s","network":"%s"}' %(groups[c],labels[c],labels[c],network_colors[network],network))
     c=c+1
   myjson = "\n".join([x for x in myjson])
   myjson = "[%s]" % myjson
   
   # Plug into the template
   template = get_template("connectogram")
   template = add_string({"CONNECTOGRAM_JSON":myjson},template)
   return template
