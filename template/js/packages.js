(function() {
  packages = {

    // Construct the package hierarchy from class names.
    // Classcounts holds the number in each class, so we know
    // where to position the label
    root: function(classes,centroids) {
      var map = {};
      function find(name, data) {
        var node = map[name], i;
        if (!node) {
          node = map[name] = data || {name: name, children: []};
          if (name.length) {
            node.parent = find(name.substring(0, i = name.lastIndexOf(".")));
            node.parent.children.push(node);
            node.key = name.substring(i + 1);
            // we need to make new x and y variables for the mni coordinates,
            // because node.x and node.y get overwritten with the x,y svg coordinates
            node.xcoord = node.x;
            node.ycoord = node.y;
            // We also are going to make an indicator variable if we should show the label  
            if (centroids.indexOf(+node.key) > -1){
              node.makelabel = 1;
            } else {
              node.makelabel = 0;
            }
          }
        }
        return node;
      }

      // Nodes go into this function ordered as in the file.  If the groupings (eg, R-1) split
      // apart the node order defined with the "order" variable, they will be broken up here
      classes.forEach(function(d) {
        find(d.name, d);
      });

      return map[""];
    },

    // Return a list of connections for the given array of nodes.
    connections: function(nodes) {
      var map = {},
          connections = [];

      // Compute a map from name to node.
      nodes.forEach(function(d) {
        map[d.name] = d;
      });

      // For each brain region construct a link from the source to target node.
      // We will save the targen and source, as well as the strength between the two
      nodes.forEach(function(d) {
        // Here are the strengths of the connections, in the same order as the connections
        var strengths;
        if (d.strength) {
          strengths = d.strength.split("|");
          for(var ii=0; ii<strengths.length; ii++) { strengths[ii] = +strengths[ii]; }
        }
      
        // Now the strengths variable holds the connection strength to connections at same index i
        if (d.connections) d.connections.forEach(function(i) {
          // i is the connection node name, and d.name is the current node name 
        if (strengths) {  
          connections.push({source: map[d.name], value: strengths.shift() ,target: map[i]});
        } 
        else {
        connections.push({source: map[d.name], value: 0 ,target: map[i]});
        }      

         });
      });

      return connections;
    },

    // Count the number in each class
    count: function(nodes) {
      
      var classes = {}; 
      var colors = {};
      // Here we will hold node keys in center of classes
      var centroids = [];

      nodes.forEach(function(d) {
        if ((d.network) in classes) 
          classes[d.network] = classes[d.network] + 1;
        else {classes[d.network] = 1; colors[d.network] = d.color;}
        });
      
      // Now let's save the keys of nodes in the middle indices for the classes
      currentclass = []
      nodes.forEach(function(d) {
        if (currentclass != d.network){
            centroids.push(d.order + Math.floor(classes[d.network] / 2));
            currentclass = d.network;
        } 
      });
      
      classcount = {classes:classes,colors:colors,centroids:centroids};
      return classcount;

    }    
  };
})();
