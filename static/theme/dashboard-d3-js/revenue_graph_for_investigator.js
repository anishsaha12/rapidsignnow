//daily data
function dailyRevenueGraph() {
  var revenueGraphMargin = {
    top: 120, right: 20, bottom:
      60, left: 60
  },
  
    revenueGraphWidth = 950 - revenueGraphMargin.left - revenueGraphMargin.right,
  
    revenueGraphHeight = 400 - revenueGraphMargin.top - revenueGraphMargin.bottom;
  
  var revenueGraphTimeFormat = d3.timeFormat("%e %B");
  
  var revenueDailyGraphXCoordinate = d3.scaleTime().range([0, revenueGraphWidth]);
  
  var revenueDailyGraphYCoordinate = d3.scaleLinear().range([revenueGraphHeight,
    0]);
  
  var revenueMonthGraphXCoordinate = d3.scaleTime().range([0, revenueGraphWidth]);
  
  var revenueMonthGraphYCoordinate = d3.scaleLinear().range([revenueGraphHeight,
    0]);
  
  // Define the axes
  
  var revenueDailyGraphXAxis = d3.axisBottom().scale(revenueDailyGraphXCoordinate).ticks(10);
  
  
  
  
  var revenueDailyGraphYAxis = d3.axisLeft().scale(revenueDailyGraphYCoordinate).ticks(5);
  
  var revenueMonthlyGraphXAxis = d3.axisBottom().scale(revenueMonthGraphXCoordinate).ticks(8);
  
  
  
  
  var revenueMonthlyGraphYAxis = d3.axisLeft().scale(revenueMonthGraphYCoordinate).ticks(5);
  
  
  
  
  // Define the line
  
  var revenueDailyGraphAxisLine = d3.line()
  
    .x(function (d) {
      return revenueDailyGraphXCoordinate(d.date);
    })
  
    .y(function (d) {
      return revenueDailyGraphYCoordinate(d.revenue);
    });
  
  var revenueMonthlyGraphAxisLine = d3.line()
  
    .x(function (d) {
      return revenueMonthGraphXCoordinate(new Date(d.month));
    })
  
    .y(function (d) {
      return revenueMonthGraphYCoordinate(d.revenue);
    });
  
  // Define the div for the tooltip
  
  var revenueToolTipDiv = d3.select("#revenueGraph").append("div")
  
    .attr("class", "tooltip").attr("id", "tooltip-for-revenue-graph")
  
    .style("opacity", 1);
  
  
  // Adds the svg canvas
  
  var revenueGraphSVG = d3.select("#revenueGraph")
  
    .append("svg")
  
    .attr("id", "svg-for-revenue-graph")
  
    .attr("width", revenueGraphWidth + revenueGraphMargin.left + revenueGraphMargin.right)
  
    .attr("height", revenueGraphHeight + revenueGraphMargin.top + revenueGraphMargin.bottom)
  
    .append("g")
  
    .attr("transform",
  
    "translate(" + revenueGraphMargin.left + "," + revenueGraphMargin.top + ")");
  // Get the data
  
  revenueGraphDailyData.forEach(function (revenueGraphDailyData) {

  revenueGraphDailyData.date = revenueGraphDailyData.date;

  revenueGraphDailyData.revenue = +revenueGraphDailyData.revenue;

  });

  // Scale the range of the data

  revenueDailyGraphXCoordinate.domain(d3.extent(revenueGraphDailyData, function (d) { return d.date; }));

  revenueDailyGraphYCoordinate.domain([0, d3.max(revenueGraphDailyData, function (d) { return d.revenue; })]);

  // Add the valueline path.

  revenueGraphSVG.append("path")

  .attr("class", "line")

  .attr("d", revenueDailyGraphAxisLine(revenueGraphDailyData));

  // Add the scatterplot

  revenueGraphSVG.selectAll("dot")

  .data(revenueGraphDailyData)

  .enter().append("circle")

  .attr("r", 3.5)

  .attr("cx", function (d) { return revenueDailyGraphXCoordinate(d.date); })

  .attr("cy", function (d) { return revenueDailyGraphYCoordinate(d.revenue); })

  .on("mouseover", function (d) {

  revenueToolTipDiv.transition()

  .duration(200)

  .style("opacity", .9);

  revenueToolTipDiv.html(revenueGraphTimeFormat(d.date) + "<br/>Revenue: $ " + d.revenue)

  .style("left", (d3.event.pageX - 270) + "px")

  .style("top", (d3.event.pageY - 28 - 2300) + "px")

  .style("display","block");

  })

  .on("mouseout", function (d) {

  revenueToolTipDiv.transition()

  .duration(500)

  .style("opacity", 0);

  });




  // Add the X Axis

  revenueGraphSVG.append("g")

  .attr("class", "x axis")

  .attr("transform", "translate(0," + revenueGraphHeight + ")")

  .call(revenueDailyGraphXAxis);




  // Add the Y Axis

  revenueGraphSVG.append("g")

  .attr("class", "y axis")

  .call(revenueDailyGraphYAxis);

  d3.select("#svg-for-revenue-graph")

  .append("text")

  .attr("transform", "rotate(-90)")

  .attr("x", -revenueGraphHeight)

  .attr("y", 25)

  .attr("dy", "-1.1em")

  .attr("text-anchor", "middle")

  .text("Revenue ( $ ) -------->");

  d3.select("#svg-for-revenue-graph")

  .append("text")

  .attr("x", 400)

  .attr("y", revenueGraphHeight + 140)

  .attr("dy", "1.5em")

  .attr("text-anchor", "middle")

  .text("Days --------->");


}




//monthly data

function monthlyRevenueGraph() {
  var revenueGraphMargin = {
    top: 120, right: 20, bottom:
      60, left: 60
  },
  
    revenueGraphWidth = 950 - revenueGraphMargin.left - revenueGraphMargin.right,
  
    revenueGraphHeight = 400 - revenueGraphMargin.top - revenueGraphMargin.bottom;
  
  var revenueGraphTimeFormat = d3.timeFormat("%e %B");
  
  var revenueDailyGraphXCoordinate = d3.scaleTime().range([0, revenueGraphWidth]);
  
  var revenueDailyGraphYCoordinate = d3.scaleLinear().range([revenueGraphHeight,
    0]);
  
  var revenueMonthGraphXCoordinate = d3.scaleTime().range([0, revenueGraphWidth]);
  
  var revenueMonthGraphYCoordinate = d3.scaleLinear().range([revenueGraphHeight,
    0]);
  
  // Define the axes
  
  var revenueDailyGraphXAxis = d3.axisBottom().scale(revenueDailyGraphXCoordinate).ticks(10);
  
  
  
  
  var revenueDailyGraphYAxis = d3.axisLeft().scale(revenueDailyGraphYCoordinate).ticks(5);
  
  var revenueMonthlyGraphXAxis = d3.axisBottom().scale(revenueMonthGraphXCoordinate).ticks(8);
  
  
  
  
  var revenueMonthlyGraphYAxis = d3.axisLeft().scale(revenueMonthGraphYCoordinate).ticks(5);
  
  
  
  
  // Define the line
  
  var revenueDailyGraphAxisLine = d3.line()
  
    .x(function (d) {
      return revenueDailyGraphXCoordinate(d.date);
    })
  
    .y(function (d) {
      return revenueDailyGraphYCoordinate(d.revenue);
    });
  
  var revenueMonthlyGraphAxisLine = d3.line()
  
    .x(function (d) {
      return revenueMonthGraphXCoordinate(new Date(d.month));
    })
  
    .y(function (d) {
      return revenueMonthGraphYCoordinate(d.revenue);
    });
  
  // Define the div for the tooltip
  
  var revenueToolTipDiv = d3.select("#revenueGraph").append("div")
  
    .attr("class", "tooltip").attr("id", "tooltip-for-revenue-graph")
  
    .style("opacity", 1);
  
  
  // Adds the svg canvas
  
  var revenueGraphSVG = d3.select("#revenueGraph")
  
    .append("svg")
  
    .attr("id", "svg-for-revenue-graph")
  
    .attr("width", revenueGraphWidth + revenueGraphMargin.left + revenueGraphMargin.right)
  
    .attr("height", revenueGraphHeight + revenueGraphMargin.top + revenueGraphMargin.bottom)
  
    .append("g")
  
    .attr("transform",
  
    "translate(" + revenueGraphMargin.left + "," + revenueGraphMargin.top + ")");
  var revenueMonthlyGraphTimeFormat = d3.timeFormat("%B");
  monthlyRevenue.forEach(function (monthlyRevenueData) {

  monthlyRevenueData.month = new Date(monthlyRevenueData.month);

  monthlyRevenueData.revenue = +monthlyRevenueData.revenue;

  });

  // Scale the range of the data

  revenueMonthGraphXCoordinate.domain(d3.extent(monthlyRevenue, function (d) { return new Date(d.month); }));

  revenueMonthGraphYCoordinate.domain([0, d3.max(monthlyRevenue, function (d) { return d.revenue; })]);

  // Add the valueline path.

  revenueGraphSVG.append("path")

    .attr("class", "line")

    .attr("d", revenueMonthlyGraphAxisLine(monthlyRevenue));

  // Add the scatterplot

  revenueGraphSVG.selectAll("dot")

    .data(monthlyRevenue)

    .enter().append("circle")

    .attr("r", 3.5)

    .attr("cx", function (d) {
      return revenueMonthGraphXCoordinate(new
        Date(d.month));
    })

    .attr("cy", function (d) {
      return revenueMonthGraphYCoordinate(d.revenue);
    })

    .on("mouseover", function (d) {

      revenueToolTipDiv.transition()

        .duration(200)

        .style("opacity", .9);

      revenueToolTipDiv.html(revenueMonthlyGraphTimeFormat(d.month) + "<br/>Revenue: $ " + d.revenue)

        .style("left", (d3.event.pageX - 270) + "px")

        .style("top", (d3.event.pageY - 28 - 2300) + "px")

        .style("display", "block");

    })

    .on("mouseout", function (d) {

      revenueToolTipDiv.transition()

        .duration(500)

        .style("opacity", 0);

    });




  // Add the X Axis

  revenueGraphSVG.append("g")

    .attr("class", "x axis")

    .attr("transform", "translate(0," + revenueGraphHeight + ")")

    .call(revenueMonthlyGraphXAxis);




  // Add the Y Axis

  revenueGraphSVG.append("g")

    .attr("class", "y axis")

    .call(revenueMonthlyGraphYAxis);


    d3.select("#svg-for-revenue-graph")

    .append("text")
  
    .attr("transform", "rotate(-90)")
  
    .attr("x", -revenueGraphHeight)
  
    .attr("y", 25)
  
    .attr("dy", "-1.1em")
  
    .attr("text-anchor", "middle")
  
    .text("Revenue ( $ ) -------->");
  
  d3.select("#svg-for-revenue-graph")
  
    .append("text")
  
    .attr("x", 400)
  
    .attr("y", revenueGraphHeight + 140)
  
    .attr("dy", "1.5em")
  
    .attr("text-anchor", "middle")
  
    .text("Months --------->");

}
