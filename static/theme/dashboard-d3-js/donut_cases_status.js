 
var dataset_for_donut_based_on_case_status = [
  {
    status:"Inactive",
    "count": case_status_inactive
},
{
  status:"In progress",
  "count": case_status_in_progress
},
{
  status:"Client called and texted",
  "count": case_status_called_and_texted
},
{
  status:"Client contacted",
  "count": case_status_client_contacted
},
{
  status:"Client Meeting Set",
  "count": case_status_client_meeting_set
},
{
  status:"Client Resceduled",
  "count": case_status_client_rescheduled
},
{
  status:"Signature obtained",
  "count":case_signature_obtained
},
{
    status:"Signature not obtained",
    "count":case_status_signature_not_obtained
},
]
dataset_for_donut_based_on_case_status.forEach(function(eachRecord) {
//console.log(eachRecord.status);
//console.log(eachRecord.count);

eachRecord.count=+eachRecord.count;
eachRecord.status=eachRecord.status;
});
var pie=d3.pie()
.value(function(d){return d.count})
.sort(null)
.padAngle(.03);

var weight_for_case_status_donut=300,height_for_case_status_donut=300;

var outerRadius_for_case_status_donut=weight_for_case_status_donut/2;
var innerRadius_for_case_status_donut=85;

var color_case_status_donut = d3.scaleOrdinal(d3.schemeCategory10);
// var color_case_status_donut=d3.scaleOrdinal()
// .range(["#BBDEFB","#396AB1","#3E9651"]);

var arc_for_case_status_donut=d3.arc()
.outerRadius(outerRadius_for_case_status_donut)
.innerRadius(innerRadius_for_case_status_donut);

var svg_for_case_status_donut=d3.select("#cases-status-donut")
.append("svg")
.attrs({
width:700,
height:400,
class:'shadow case-status-donut'
})
.styles({
'padding-top':'10px',
'padding-left':'30px',
}).append('g')
.attrs({
transform:'translate('+w/2+','+h/2+')',
class:'case-status-donut',
})
var path=svg_for_case_status_donut.selectAll('path')
.data(pie(dataset_for_donut_based_on_case_status))
.enter()
.append('path')
.attrs({
d:arc_for_case_status_donut,
fill:function(d,i){
  //console.log(d.data.status)
  return color_case_status_donut(d.data.status);
},
id:function(d,i){
  status = d.data.status
  status = status.toLowerCase()
  status = status.replace(/\s/g, '-');
  return status
}, 
}).styles({
fill:function(d,i){
  //console.log(d.data.status)
  return color_case_status_donut(d.data.status);
},


});;


path.transition()
.duration(1000)
.attrTween('d', function(d) {
var interpolate = d3.interpolate({startAngle: 0, endAngle: 0}, d);
return function(t) {
  return arc_for_case_status_donut(interpolate(t));
};
});


var restOfTheData=function(){
var text_for_case_status_donut=svg_for_case_status_donut.selectAll('text')
.data(pie(dataset_for_donut_based_on_case_status))
.enter()
.append("text")
.transition()
.duration(200)
.attrs({
    "transform": function (d) {
    return "translate(" + arc_for_case_status_donut.centroid(d) + ")";   
      },
id:function(d,i){
  status = d.data.status
  status = status.toLowerCase()
  status = status.replace(/\s/g, '-');
  return status + "-text"
  },
  "dy":".4em",
  "text-anchor":"middle",
})
//   .attrs("dy", ".4em")
//   .attrs("text-anchor", "middle")
.text(function(d){
    return d.data.count+"%";
})
.styles({
    fill:'#fff',
    'font-size':'13px',
    'font-weight':'bold',
});

var legendRectSize=20;
var legendSpacing=7;
var legendHeight=legendRectSize+legendSpacing;


var legend_for_case_status_donut=svg_for_case_status_donut.selectAll('.case-status-donut')
.data(color_case_status_donut.domain())
.enter()
.append('g')
.attrs({
    transform:function(d,i){
        //Just a calculation for x & y position
        return 'translate(175,' + ((i*legendHeight)-115) + ')';
    },
    class:'legend-case-status-donut',
});

legend_for_case_status_donut.append('rect')
.attrs({
    width:legendRectSize,
    height:legendRectSize,
    rx:20,
    ry:20
})
.styles({
    fill:color_case_status_donut,
    stroke:color_case_status_donut
});

legend_for_case_status_donut.append('text')
.data(pie(dataset_for_donut_based_on_case_status))
.attrs({
    x:30,
    y:15,
})
.text(function(d){
    return d.data.status;
}).styles({
    fill:'black',
    'font-size':'14px'

});
};

setTimeout(restOfTheData,1000);