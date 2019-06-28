angular.module("CAMEL")
    .controller('HomeController', function($location, $routeParams, $route, $scope, Experiment, Field) {
	var ctrl = this;
	
	ctrl.experiments = Experiment.query(function(){
	    ctrl.experiment_count = ctrl.experiments.length;
	});

	//custom grid to fit species labels
	ctrl.speciesGrid = {
	    left: 50,
	    top: 30,
	    right: 20,
	    bottom: 150
	};
	
    });
