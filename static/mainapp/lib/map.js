// The svg
var svg = d3.select("svg#map"),
    width = +svg.attr("width"),
    height = +svg.attr("height");

// Map and projection
var projection = d3.geo.mercator()
    .center([20, 48])                // GPS of location to zoom on
    .scale(1000)                       // This is like the zoom
    .translate([ width/2, height/2 ])

// Load external data and boot
d3.json("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson", function(data){

    // Filter data
    // data.features = data.features.filter(function(d){console.log(d.properties.name) ; return d.properties.name=="Europe"})

    // Draw the map
    svg.append("g")
        .selectAll("path")
        .data(data.features)
        .enter()
        .append("path")
          .attr("fill", "grey")
          .attr("d", d3.geo.path()
              .projection(projection)
          )
        .style("stroke", "none")

});

