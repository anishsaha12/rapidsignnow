function getMax(arr, prop) {
    var max;
    for (var i=0 ; i<arr.length ; i++) {
        if (!max || parseInt(arr[i][prop]) > parseInt(max[prop]))
            max = arr[i];
    }
    return max[prop];
}
// function getMax(arr, prop) {
//     var max;
//     for (var i=0 ; i<arr.length ; i++) {
//         if (!max || parseInt(arr[i][prop]) > parseInt(max[prop]))
//             max = arr[i];
//     }
//     return max[prop];
// }

var casesAddedClosedMargin = { top: 120, right: 20, bottom: 60, left: 40 },
    casesAddedClosedWidth = 900 - casesAddedClosedMargin.left - casesAddedClosedMargin.right,
    casesAddedClosedHeight = 400 - casesAddedClosedMargin.top - casesAddedClosedMargin.bottom;

// Parse the date / time
// var casesAddedClosedParseDate = d3.timeParse("%d-%b-%y");
var casesAddedClosedFormatTime = d3.timeFormat("%e %B");

// Set the ranges
var casesAddedxCoordinate = d3.scaleTime().range([0, casesAddedClosedWidth]);
var casesAddedyCoordinate = d3.scaleLinear().range([casesAddedClosedHeight, 0]);
var casesClosedxCoordinate = d3.scaleTime().range([0, casesAddedClosedWidth]);
var casesClosedyCoordinate = d3.scaleLinear().range([casesAddedClosedHeight, 0]);
// Define the axes
var casesAddedxAxis = d3.axisBottom().scale(casesAddedxCoordinate).ticks(10);

var casesAddedyAxis = d3.axisLeft().scale(casesAddedyCoordinate).ticks(5);
var casesClosedxAxis = d3.axisBottom().scale(casesClosedxCoordinate).ticks(10);

var casesClosedyAxis = d3.axisLeft().scale(casesClosedyCoordinate).ticks(5);

// Define the line
var casesAddedClosedAxisLine = d3.line()
    .x(function (d) { return casesAddedxCoordinate(d.date); })
    .y(function (d) { return casesAddedyCoordinate(d.cases); });

// Define the div for the tooltip
var casesAddedClosedDiv = d3.select("#graph-based-on-cases-added-closed").append("div")
    .attr("class", "tooltip").attr("id", "tooltip-for-cases-added-closed-graph")
    .style("opacity", 1);

// Adds the svg canvas
var casesAddedClosedSVG = d3.select("#graph-based-on-cases-added-closed")
    .append("svg")
    .attr("id","svg-for-cases-added-closed-graph")
    .attr("width", casesAddedClosedWidth + casesAddedClosedMargin.left + casesAddedClosedMargin.right)
    .attr("height", casesAddedClosedHeight + casesAddedClosedMargin.top + casesAddedClosedMargin.bottom)
    .append("g")
    .attr("transform",
    "translate(" + casesAddedClosedMargin.left + "," + casesAddedClosedMargin.top + ")");

// Get the data
addedCaseData.forEach(function (casesAddedData) {

    casesAddedData.date = casesAddedData.date;
    casesAddedData.cases = +casesAddedData.cases;
});

// Scale the range of the data
casesAddedxCoordinate.domain(d3.extent(addedCaseData, function (d) { return d.date; }));


if (getMax(addedCaseData,"cases") > getMax(closedCaseData,"cases"))
{casesAddedyCoordinate.domain([0, d3.max(addedCaseData, function (d) { return d.cases; })]);}
else
{casesAddedyCoordinate.domain([0, d3.max(closedCaseData, function(d) { return d.cases; })]); }

// Add the valueline path.


casesAddedClosedSVG.append("path")
    .attr("class", "line")
    .attr("d", casesAddedClosedAxisLine(addedCaseData));

// Add the scatterplot
casesAddedClosedSVG.selectAll("dot")
    .data(addedCaseData)
    .enter().append("circle")
    .attr("r", 3.5)
    .attr("cx", function (d) { return casesAddedxCoordinate(d.date); })
    .attr("cy", function (d) { return casesAddedyCoordinate(d.cases); })
    .on("mouseover", function (d) {
        casesAddedClosedDiv.transition()
            .duration(200)
            .style("opacity", .9);
        casesAddedClosedDiv.html(casesAddedClosedFormatTime(d.date) + "<br/>Cases Added: " + d.cases)
            .style("left", (d3.event.pageX - 270) + "px")
            .style("top", (d3.event.pageY - 28 - 50) + "px")
            .style("display","block");
    })
    .on("mouseout", function (d) {
        casesAddedClosedDiv.transition()
            .duration(500)
            .style("opacity", 0);
    });

// Add the X Axis
casesAddedClosedSVG.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + casesAddedClosedHeight + ")")
    .call(casesAddedxAxis);

// Add the Y Axis
casesAddedClosedSVG.append("g")
    .attr("class", "y axis")
    .call(casesAddedyAxis);

//closed data
closedCaseData.forEach(function (casesClosedData) {

    casesClosedData.date = casesClosedData.date;
    casesClosedData.cases = +casesClosedData.cases;
});

// Scale the range of the data
// casesAddedxCoordinate.domain(d3.extent(closedCaseData, function(d) { return d.date; }));
// casesAddedyCoordinate.domain([0, d3.max(closedCaseData, function(d) { return d.cases; })]); 

// Add the valueline path.


casesAddedClosedSVG.append("path")
    .attr("class", "line1")
    .attr("d", casesAddedClosedAxisLine(closedCaseData));

// Add the scatterplot
casesAddedClosedSVG.selectAll("dot")
    .data(closedCaseData)
    .enter().append("circle")
    .attr("r", 3.5)
    .attr("cx", function (d) { return casesAddedxCoordinate(d.date); })
    .attr("cy", function (d) { return casesAddedyCoordinate(d.cases); })
    .on("mouseover", function (d) {
        casesAddedClosedDiv.transition()
            .duration(200)
            .style("opacity", .9);
        casesAddedClosedDiv.html(casesAddedClosedFormatTime(d.date) + "<br/>Cases Closed: " + d.cases)
            .style("left", (d3.event.pageX - 270) + "px")
            .style("top", (d3.event.pageY - 28 - 50) + "px")
            .style("display","block");
    })
    .on("mouseout", function (d) {
        casesAddedClosedDiv.transition()
            .duration(500)
            .style("opacity", 0);
    });

// Add the X Axis
casesAddedClosedSVG.append("g")
    .attr("class", "x axis")
    .attr("transform", "translate(0," + casesAddedClosedHeight + ")")
    .call(casesAddedxAxis);

// Add the Y Axis
casesAddedClosedSVG.append("g")
    .attr("class", "y axis")
    .call(casesAddedyAxis);


d3.select("#svg-for-cases-added-closed-graph")
.append("text")
.attr("transform", "rotate(-90)")
.attr("x", -casesAddedClosedHeight)
.attr("y", 23)
.attr("dy", "-1.1em")
.attr("text-anchor", "middle")
.text("No of Cases  -------->");


d3.select("#svg-for-cases-added-closed-graph")
.append("text")
.attr("x", 400)
.attr("y", casesAddedClosedHeight + 140)
.attr("dy", "1.5em")
.attr("text-anchor", "middle")
.text("Days  --------->");