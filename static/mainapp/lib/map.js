//tooltip function
async function drawMap(dataFeatures){
    // The svg
    var svg = d3.select("svg#map"),
        width = +svg.attr("width"),
        height = +svg.attr("height");

    // Map and projection
    var projection = d3.geo.mercator()
        .center([20, 48])                // GPS of location to zoom on
        .scale(1000)                     // This is like the zoom
        .translate([ width/2, height/2 ])

    var blues = ["#154360", "#1f618d", "#2980b9", "#7fb3d5"];
    var colorScale = d3.scale.ordinal().range(blues);

    // Load external data and boot
    d3.json("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson", function(data){

        // Filter data
        //data.features = data.features.filter(function(d){
            //console.log(d.properties.name); 
            //return d.properties.name=="Italy";
        //})
        
        const dataMap = new Map(dataFeatures.map(d => [d.name, d.value]));
        
        //console.log(dataMap);

        // Draw the map
        svg.append("g")
            .selectAll("path")
            .data(data.features)
            .enter()
            .append("path")
            .attr("fill", "#154360")
            .attr("d", d3.geo.path()
                .projection(projection)   
            )
            .attr("fill", d => {
                // Use the feature's id to look up the value
                //console.log(d);
                const value = dataMap.get(d.properties.name);
                return value ? colorScale(value) : "#ccc"; // colorScale is your D3 color 
            })
            .on("mouseover", function(event, d) {
                d3.select(this)
                .attr("fill", d => {
                    const val = dataMap.get(d.properties.name);
                    return val != null ? "black" : "#ccc";
                  })  // Change to highlight color on hover
            })
            .on("mouseout", function(event, d) {
                d3.select(this)
                .attr("fill", d => {
                    const val = dataMap.get(d.properties.name);
                    return val != null ? colorScale(val) : "#ccc";
                });  // Reset to original color
            }) 
            .style("stroke", "none");
    });
};
