angular.module("CAMEL")
    .controller('HomeController', function($location, $routeParams, $route, Experiment, Field) {
	var ctrl = this;
	
	ctrl.experiments = Experiment.query(function(){
	    ctrl.experiment_count = ctrl.experiments.length;
	});
});
