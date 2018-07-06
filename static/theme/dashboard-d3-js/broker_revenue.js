function dailyBrokerRevenueGraph(broker_id) {
  for (i=0;i<brokerCount;i++)
{
  if ( brokerRevenue[i].id == broker_id )
  {
    brokerRevenueGraphDailyData = brokerRevenue[i].revenue
  var brokerRevenueGraphMargin = {
    top: 120, right: 20, bottom:
      60, left: 60
  },
  
    brokerRevenueGraphWidth = 950 - brokerRevenueGraphMargin.left - brokerRevenueGraphMargin.right,
  
    brokerRevenueGraphHeight = 400 - brokerRevenueGraphMargin.top - brokerRevenueGraphMargin.bottom;
  
  var brokerRevenueGraphTimeFormat = d3.timeFormat("%e %B");
  
  var brokerRevenueDailyGraphXCoordinate = d3.scaleTime().range([0, brokerRevenueGraphWidth]);
  
  var brokerRevenueDailyGraphYCoordinate = d3.scaleLinear().range([brokerRevenueGraphHeight,
    0]);
  
  var brokerRevenueMonthGraphXCoordinate = d3.scaleTime().range([0, brokerRevenueGraphWidth]);
  
  var brokerRevenueMonthGraphYCoordinate = d3.scaleLinear().range([brokerRevenueGraphHeight,
    0]);
  
  // Define the axes
  
  var brokerRevenueDailyGraphXAxis = d3.axisBottom().scale(brokerRevenueDailyGraphXCoordinate).ticks(10);
  
  
  
  
  var brokerRevenueDailyGraphYAxis = d3.axisLeft().scale(brokerRevenueDailyGraphYCoordinate).ticks(5);
  
  var brokerRevenueMonthlyGraphXAxis = d3.axisBottom().scale(brokerRevenueMonthGraphXCoordinate).ticks(8);
  
  
  
  
  var brokerRevenueMonthlyGraphYAxis = d3.axisLeft().scale(brokerRevenueMonthGraphYCoordinate).ticks(5);
  
  
  
  
  // Define the line
  
  var brokerRevenueDailyGraphAxisLine = d3.line()
  
    .x(function (d) {
      return brokerRevenueDailyGraphXCoordinate(d.date);
    })
  
    .y(function (d) {
      return brokerRevenueDailyGraphYCoordinate(d.revenue);
    });
  
  // Define the div for the tooltip
  
  var brokerRevenueToolTipDiv = d3.select("#brokerRevenueGraph").append("div")
  
    .attr("class", "tooltip").attr("id", "tooltip-for-broker-revenue-graph")
  
    .style("opacity", 1);
  
  
  // Adds the svg canvas
  
  var brokerRevenueGraphSVG = d3.select("#brokerRevenueGraph")
  
    .append("svg")
  
    .attr("id", "svg-for-broker-revenue-graph")
  
    .attr("width", brokerRevenueGraphWidth + brokerRevenueGraphMargin.left + brokerRevenueGraphMargin.right)
  
    .attr("height", brokerRevenueGraphHeight + brokerRevenueGraphMargin.top + brokerRevenueGraphMargin.bottom)
  
    .append("g")
  
    .attr("transform",
  
    "translate(" + brokerRevenueGraphMargin.left + "," + brokerRevenueGraphMargin.top + ")");
  // Get the data
  
  brokerRevenueGraphDailyData.forEach(function (brokerRevenueGraphDailyData) {

  brokerRevenueGraphDailyData.date = brokerRevenueGraphDailyData.date;

  brokerRevenueGraphDailyData.revenue = +brokerRevenueGraphDailyData.revenue;

  });

  // Scale the range of the data

  brokerRevenueDailyGraphXCoordinate.domain(d3.extent(brokerRevenueGraphDailyData, function (d) { return d.date; }));

  brokerRevenueDailyGraphYCoordinate.domain([0, d3.max(brokerRevenueGraphDailyData, function (d) { return d.revenue; })]);

  // Add the valueline path.

  brokerRevenueGraphSVG.append("path")

  .attr("class", "line")

  .attr("d", brokerRevenueDailyGraphAxisLine(brokerRevenueGraphDailyData));

  // Add the scatterplot

  brokerRevenueGraphSVG.selectAll("dot")

  .data(brokerRevenueGraphDailyData)

  .enter().append("circle")

  .attr("r", 3.5)

  .attr("cx", function (d) { return brokerRevenueDailyGraphXCoordinate(d.date); })

  .attr("cy", function (d) { return brokerRevenueDailyGraphYCoordinate(d.revenue); })

  .on("mouseover", function (d) {

  brokerRevenueToolTipDiv.transition()

  .duration(200)

  .style("opacity", .9);

  brokerRevenueToolTipDiv.html(brokerRevenueGraphTimeFormat(d.date) + "<br/>Revenue: $ " + d.revenue)

  .style("left", (d3.event.pageX - 270) + "px")

  .style("top", (d3.event.pageY - 28 - 2360) + "px")

  .style("display","block");

  })

  .on("mouseout", function (d) {

  brokerRevenueToolTipDiv.transition()

  .duration(500)

  .style("opacity", 0);

  });




  // Add the X Axis

  brokerRevenueGraphSVG.append("g")

  .attr("class", "x axis")

  .attr("transform", "translate(0," + brokerRevenueGraphHeight + ")")

  .call(brokerRevenueDailyGraphXAxis);




  // Add the Y Axis

  brokerRevenueGraphSVG.append("g")

  .attr("class", "y axis")

  .call(brokerRevenueDailyGraphYAxis);

  d3.select("#svg-for-broker-revenue-graph")

  .append("text")

  .attr("transform", "rotate(-90)")

  .attr("x", -brokerRevenueGraphHeight)

  .attr("y", 25)

  .attr("dy", "-1.1em")

  .attr("text-anchor", "middle")

  .text("Revenue ( $ ) -------->");

  d3.select("#svg-for-broker-revenue-graph")

  .append("text")

  .attr("x", 400)

  .attr("y", brokerRevenueGraphHeight + 140)

  .attr("dy", "1.5em")

  .attr("text-anchor", "middle")

  .text("Days --------->");

  }
  }


}



