function dashboard(id,id2,fDataObject){
    var barColor = 'steelblue';
	var fData = fDataObject.data
    function segColor(c){ return {Yes:"#41ab5d", No:"#e08214",NotReported:"#807dba",TBD:"#307dba"}[c]; }
    
    // compute total for each Work Plan Area.
    fData.forEach(function(d){d.total=d.perform.Yes+d.perform.No+d.perform.NotReported+d.perform.TBD;});
    
    // function to handle pieChart.
    function pieChart(pD){
        var pC ={},    pieDim ={w:200, h: 200};
        pieDim.r = Math.min(pieDim.w, pieDim.h) / 2;
                
        // create svg for pie chart.
        var piesvg = d3.select(id).append("svg")
            .attr("width", pieDim.w).attr("height", pieDim.h).append("g")
            .attr("transform", "translate("+pieDim.w/2+","+pieDim.h/2+")");
        
        // create function to draw the arcs of the pie slices.
        var arc = d3.svg.arc().outerRadius(pieDim.r - 10).innerRadius(0);

        // create a function to compute the pie slice angles.
        var pie = d3.layout.pie().sort(null).value(function(d) { return d.perform; });

        // Draw the pie slices.
        piesvg.selectAll("path").data(pie(pD)).enter().append("path").attr("d", arc)
            .each(function(d) { this._current = d; })
            .style("fill", function(d) { return segColor(d.data.type); });
    }
    
    // function to handle legend.
    function legend(lD){
        var leg = {};
            
        // create table for legend.
        var legend = d3.select(id).append("table").attr('class','legend');
        
        // create one row per segment.
        var tr = legend.append("tbody").selectAll("tr").data(lD).enter().append("tr");
			
        // create the first column for each segment.
        tr.append("td").append("svg").attr("width", '12').attr("height", '12').append("rect")
            .attr("width", '12').attr("height", '12')
			.attr("fill",function(d){ return segColor(d.type); });
            
        // create the second column for each segment.
        tr.append("td").text(function(d){ return d.type;});

        // create the third column for each segment.
        tr.append("td").attr("class",'legendFreq')
            .text(function(d){ return d3.format(",")(d.perform);});

        // create the fourth column for each segment.
        tr.append("td").attr("class",'legendPerc')
            .text(function(d){ return getLegend(d,lD);});

        // Utility function to be used to update the legend.
        leg.update = function(nD){
            // update the data attached to the row elements.
            var l = legend.select("tbody").selectAll("tr").data(nD);

            // update the performs.
            l.select(".legendFreq").text(function(d){ return d3.format(",")(d.perform);});

            // update the percentage column.
            l.select(".legendPerc").text(function(d){ return getLegend(d,nD);});        
        }
        
        function getLegend(d,aD){ // Utility function to compute percentage.
            return d3.format("%")(d.perform/d3.sum(aD.map(function(v){ return v.perform; })));
        }

        return leg;
    }
	
	// function to handle liquidFillGauge.
    function createBullet(lD){
		var margin = {top: 10, right: 40, bottom: 20, left: 60},
		width = $("#bullet-A").width() - margin.left - margin.right,
		height = 60 - margin.top - margin.bottom;
                
        // create svg for bullet.
		var divRowLFG = "";
		$.each(lD,function(index,value){
			wpa = value[0].split(": ")[0];
			wpaName = value[0].split(": ")[1];
			per_value = value[1];
			
			divBullet = "divBullet-"+wpa;
			divBulletRow = "divBulletRow-"+wpa;
			var bullettxtdiv = d3.select(id2).append("div").attr("id",divBulletRow).attr("class","row row-Bullet").append("div").attr("class","col-xs-12 col-sm-12 col-md-12 col-lg-12").html('<h3><small>'+value[0]+'</small></h3>');
			var bulletdiv = d3.select("#"+divBulletRow).append("div").attr("id",divBullet).attr("class","col-xs-12 col-sm-12 col-md-12 col-lg-12");			
			
			var bulletBar = d3.bullet().width(width).height(height);
			if(isNaN(per_value)){
				var data = [{"title":"N/A *","subtitle":"","ranges":[0,0,100],"measures":[0,0],"markers":[0]}];
			}
			else{
				var data = [{"title":per_value.toFixed(0)+"%","subtitle":"","ranges":[0,0,100],"measures":[per_value,100],"markers":[0]}];
			}
			var svg = d3.select("#"+divBullet).selectAll("svg").data(data).enter().append("svg")
				.attr("class", "bullet")
				.attr("width", width + margin.left + margin.right)
				.attr("height", height + margin.top + margin.bottom)
				.append("g")
				.attr("transform", "translate(" + margin.left + "," + margin.top + ")")
				.call(bulletBar.duration(1000));
			  
			var title = svg.append("g")
				.style("text-anchor", "end")
				.attr("transform", "translate(-6," + height / 2 + ")");

			title.append("text")
				.attr("class", "title")
				.text(function(d) { return d.title; });

			title.append("text")
				.attr("class", "subtitle")
				.attr("dy", "1em")
				.text(function(d) { return d.subtitle; });
		});
    }
    
    // calculate total perform by segment for all Org.
    var tF = ['Yes','No','NotReported','TBD'].map(function(d){ 
        return {type:d, perform: d3.sum(fData.map(function(t){ return t.perform[d];}))}; 
    });    
    
    // calculate total perform by Work Plan Area for all segment.
    var sF = fData.map(function(d){return [d.WPA,d.perform.Yes/d.total*100];});
	
	// calculate percent of goals reached for each Work Plan Area
	var lF = fData.map(function(d){return [d.WPA+": "+d.WPA_name,d.perform.Yes/d.total*100]});

    var pC = pieChart(tF), // create the pie-chart.
        leg= legend(tF);
		lBullet = createBullet(lF);  // create the legend.
}