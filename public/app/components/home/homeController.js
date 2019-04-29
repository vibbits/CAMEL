angular.module("CAMEL")
    .controller('HomeController', function($location, $routeParams, $route, Experiment, Field) {
	var ctrl = this;
	
	ctrl.experiments = Experiment.query(function(){
	    ctrl.experiment_count = ctrl.experiments.length;
	});

	
	
	speciesStats = Field.get({'id': 'Species'}, function(){
	    var myChart = echarts.init(document.getElementById('chart-species'));

	    const colNr = 8;
	    counts = speciesStats.values.slice(0,colNr);
	    
	    topSpecies = counts.map(x => x.value);
	    topSpeciesCounts = counts.map(x => x.number);
	    	    
	    myChart.setOption({
		tooltip: {},
		xAxis: {
		    data: topSpecies,
		    axisLabel: {
			rotate: 45
		    }
		},
		yAxis: {
		    name: "# experiments"
		},
		series: [{
		    name: 'species',
		    type: 'bar',
		    data: topSpeciesCounts
		}]
	    });
	    
	});
		
    });
