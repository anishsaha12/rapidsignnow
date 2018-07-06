var width = 900;
var height = 500;

var lowColor = '#f9f9f9'
var highColor = '#bc2a66'

// D3 Projection
var projection = d3.geoAlbersUsa()
  .translate([width / 2, height / 2]) // translate to center of screen
  .scale([1000]); // scale things down so see entire US

// Define path generator
var path = d3.geoPath() // path generator that will convert GeoJSON to SVG paths
  .projection(projection); // tell path generator to use albersUsa projection

var mapTooltip = d3.select("#map-data").append("div")
.attr("class", "tooltip").attr("id", "tooltip-for-map-data")
.style("opacity", 1);
//Create SVG element and append map to the SVG
var svg = d3.select("#map-data")
  .append("svg")
  .attr("width", width)
  .attr("height", height);

// Load in my states data!
function map(data) {
    data = mapData
    var dataArray = [];
	for (var d = 0; d < data.length; d++) {
		dataArray.push(parseFloat(data[d].value))
	}
	var minVal = d3.min(dataArray)
	var maxVal = d3.max(dataArray)
	var ramp = d3.scaleLinear().domain([minVal,maxVal]).range([lowColor,highColor])
	
  // Load GeoJSON data and merge with states data  
  // d3.json("https://gist.githubusercontent.com/michellechandra/0b2ce4923dc9b5809922/raw/a476b9098ba0244718b496697c5b350460d32f99/us-states.json", function(json) {
    d3.json(us_states_link, function(json) {
    // Loop through each state data value in the .csv file
    for (var i = 0; i < data.length; i++) {

      // Grab State Name
      var dataState = data[i].state;

      // Grab data value 
      var dataValue = data[i].value;

      // Find the corresponding state inside the GeoJSON
      for (var j = 0; j < json.features.length; j++) {
        var jsonState = json.features[j].properties.name;

        if (dataState == jsonState) {

          // Copy the data value into the JSON
          json.features[j].properties.value = dataValue;

          // Stop looking through the JSON
          break;
        }
      }
    }

    // Bind the data to the SVG and create one path per GeoJSON feature
    svg.selectAll("path")
      .data(json.features)
      .enter()
      .append("path")
      .attr("d", path)
      .style("stroke", "#fff")
      .style("stroke-width", "1")
      .style("fill", function(d) { return ramp(d.properties.value) })
      .on("mouseover", function (d) {
        mapTooltip.transition()
              .duration(200)
              .style("opacity", .9);
              mapTooltip.html(d.properties.name.toUpperCase() + "<br/>Cases: " + d.properties.value + "</br> Percent: " + ((d.properties.value * 100) / total_cases).toFixed(2))
              .style("left", (d3.event.pageX - 270) + "px")
              .style("top", (d3.event.pageY - 28 - 3640) + "px")
              .style("display","block");
      })
      .on("mouseout", function (d) {
        mapTooltip.transition()
              .duration(500)
              .style("opacity", 0);
      });
  
    
      // add a legend
		var w = 140, h = 300;

		var key = d3.select("#map-data")
			.append("svg")
			.attr("width", w)
			.attr("height", h)
            .attr("class", "legend")
        key.append("text").text("No of cases").attr("x", 0)
        .attr("y",10)
		var legend = key.append("defs")
			.append("svg:linearGradient")
			.attr("id", "gradient")
			.attr("x1", "100%")
			.attr("y1", "0%")
			.attr("x2", "100%")
			.attr("y2", "100%")
			.attr("spreadMethod", "pad");

		legend.append("stop")
			.attr("offset", "0%")
			.attr("stop-color", highColor)
			.attr("stop-opacity", 1);
			
		legend.append("stop")
			.attr("offset", "100%")
			.attr("stop-color", lowColor)
			.attr("stop-opacity", 1);

		key.append("rect")
			.attr("width", w - 100)
			.attr("height", h)
			.style("fill", "url(#gradient)")
			.attr("transform", "translate(0,15)");

		var y = d3.scaleLinear()
			.range([h, 0])
			.domain([minVal, maxVal]);

		var yAxis = d3.axisRight(y);

		key.append("g")
			.attr("class", "y axis")
			.attr("transform", "translate(41,15)")
			.call(yAxis)
  });
};