angular.module("CAMEL")
    .directive('countChart', function($location, Field) {
	return {
	    restrict: 'E',
	    templateUrl: 'app/shared/countChart/countChart.html',
	    scope: {
		fieldTitle: '@',
		colNr: '@',
		chartHeight: '@?',
		customGrid: '=?'
	    },
	    link: function(scope, elem, attr){
		//set default chart height
		if (!scope.hasOwnProperty('chartHeight')){
		    scope.chartHeight = "500px";
		}

		
		var valueStats = Field.get({'id': scope.fieldTitle}, function(){
		    speciesChart = echarts.init(document.getElementById('chart-'+scope.fieldTitle));
		    
		    counts = valueStats.values.slice(0,scope.colNr);
		    
		    topValues = counts.map(x => x.value);
		    topCounts = counts.map(x => x.number);

		    options = {
			tooltip: {},
			xAxis: {
			    data: topValues,
			    axisLabel: {
				rotate: 45
			    }
			},
			yAxis: {
			    name: "# experiments"
			},
			series: [{
			    name: scope.fieldTitle,
			    type: 'bar',
			    data: topCounts
			}]
		    };
		    
		    if (scope.hasOwnProperty('customGrid')){
			options.grid = scope.customGrid;		    
		    }
		    
		    speciesChart.setOption(options);
		});
	    }
	}
    });
