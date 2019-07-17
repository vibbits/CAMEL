angular.module("CAMEL")
    .directive('distChart', function($location, Field) {
	return {
	    restrict: 'E',
	    templateUrl: 'app/shared/distChart/distChart.html',
	    scope: {
		fieldTitle: '@',		
		unit: '@?',
		binNumber: '@',
		min: '@?',
		max: '@?',
		chartHeight: '@?',
	    },
	    link: function(scope, elem, attr){
		//set default chart height
		if (!scope.hasOwnProperty('unit')){
		    scope.unit = "";
		}
		if (!scope.hasOwnProperty('chartHeight')){
		    scope.chartHeight = "500px";
		}
		
		var wgsStats = Field.get({'id': scope.fieldTitle}, function(){
		    
		    var wgsChart = echarts.init(document.getElementById('chart-'+scope.fieldTitle));
	    	    
		    values = wgsStats.values;

		    var max = values[0].value;
		    var min = values[0].value;
		    for (var v in values){
			if (values.hasOwnProperty(v)){
			    var valuePair = values[v];
			    var value = valuePair.value;
			    max = Math.max(max, value);
			    min = Math.min(min, value);
			}
		    }

		    if (!scope.hasOwnProperty('min')){
			scope.min = min;
		    }
		    if (!scope.hasOwnProperty('max')){
			scope.max = max;
		    }

		    scope.binNumber = (+scope.binNumber);
		    scope.max = (+scope.max);
		    scope.min = (+scope.min);
		    
		    var valueRange = scope.max - scope.min;
		    var binSize = Math.round(valueRange / scope.binNumber);
		    var binBounds = new Array(scope.binNumber);
		    for (var i=0; i<scope.binNumber; i++){
			binBounds[i] = scope.min + (i+1)*binSize;
		    }
		    binBounds[0] = "<"+binBounds[0];
		    binBounds[scope.binNumber-1] = binBounds[scope.binNumber-1]+"<"
		    var bins = new Array(scope.binNumber);
		    for (var i=0; i<scope.binNumber; i++){
			bins[i] = 0;
		    }
		    for (var v in values){	
			if (values.hasOwnProperty(v)){
			    var valuePair = values[v];
			    var value = valuePair.value;
			    var occur = valuePair.number;
			    binNr = Math.floor((value-scope.min)/binSize);
			    if (binNr < scope.binNumber){
				bins[binNr]+= occur;
			    } else {
				bins[scope.binNumber-1]+= occur;
			    }
			}
		    }
		    
		    datalines = {
			data: bins,
			type: 'line',
			smooth: true
		    };
		    
		    wgsChart.setOption({
			tooltip: {
			    trigger: 'axis'
			},
			xAxis: {
			    name: scope.unit,
			    type: 'category',
			    data: binBounds
			},
			yAxis: {
			    name: '# experiments',
			    type: 'value'
			},
			series: datalines
		    });
		    
		});	
	    }
	}
});
