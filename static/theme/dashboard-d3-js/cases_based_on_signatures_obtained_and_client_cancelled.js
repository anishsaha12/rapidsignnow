 
var dataset_for_donut_based_on_signature = [
        {
            status:"Client cancelled",
            "count": client_cancelled_count
        },
        {
            status:"Signature obtained",
            "count":signature_obtained_count
        },
        {
            status:"Signature not obtained",
            "count":signature_not_obtained_count
        },
        {
            status:"Others",
            "count":others
        }

 ]
 dataset_for_donut_based_on_signature.forEach(function(eachRecord) {
    //console.log(eachRecord.status);
    //console.log(eachRecord.count);

      eachRecord.count=+eachRecord.count;
      eachRecord.status=eachRecord.status;
    });
var pie=d3.pie()
.value(function(d){return d.count})
.sort(null)
.padAngle(.03);

var w=300,h=300;

var outerRadius=w/2;
var innerRadius=85;

var color_for_donut_based_on_signature = d3.scaleOrdinal(d3.schemeCategory10);
// var color_for_donut_based_on_signature=d3.scaleOrdinal()
// .range(["#BBDEFB","#396AB1","#3E9651"]);

var arc=d3.arc()
.outerRadius(outerRadius)
.innerRadius(innerRadius);

var svg_for_donut_based_on_signature=d3.select("#cases-based-on-signature-obtained")
.append("svg")
.attrs({
    width:550,
    height:400,
    class:'shadow'
})
.styles({
    'padding-top':'10px',
    'padding-left':'10px',
}).append('g')
.attrs({
    transform:'translate('+w/2+','+h/2+')',
    class:'legend',
})
var path=svg_for_donut_based_on_signature.selectAll('path')
.data(pie(dataset_for_donut_based_on_signature))
.enter()
.append('path')
.attrs({
    d:arc,
    fill:function(d,i){
        //console.log(d.data.status)
        return color_for_donut_based_on_signature(d.data.status);
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
        return color_for_donut_based_on_signature(d.data.status);
    },
    

});;


path.transition()
.duration(1000)
.attrTween('d', function(d) {
    var interpolate = d3.interpolate({startAngle: 0, endAngle: 0}, d);
    return function(t) {
        return arc(interpolate(t));
    };
});


var restOfTheData=function(){
  var text=svg_for_donut_based_on_signature.selectAll('text')
      .data(pie(dataset_for_donut_based_on_signature))
      .enter()
      .append("text")
      .transition()
      .duration(200)
      .attrs({
          "transform": function (d) {
          return "translate(" + arc.centroid(d) + ")";   
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


  var legend=svg_for_donut_based_on_signature.selectAll('.legend')
      .data(color_for_donut_based_on_signature.domain())
      .enter()
      .append('g')
      .attrs({
          class:'legend',
          transform:function(d,i){
              //Just a calculation for x & y position
              return 'translate(175,' + ((i*legendHeight)-115) + ')';
          }
      });
  legend.append('rect')
      .attrs({
          width:legendRectSize,
          height:legendRectSize,
          rx:20,
          ry:20
      })
      .styles({
          fill:color_for_donut_based_on_signature,
          stroke:color_for_donut_based_on_signature
      });

  legend.append('text')
  .data(pie(dataset_for_donut_based_on_signature))    
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