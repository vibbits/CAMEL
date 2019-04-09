angular.module("CAMEL")
    .controller('ExperimentsController', function($scope, $location, $timeout, $routeParams, $route, $http, Experiment, Field) {
	var ctrl = this;
	var showNr = 5;
	
	ctrl.fields = Field.query(function(){
	    for (i in ctrl.fields){
		if (i<showNr){
		    ctrl.fields[i].show = true;
		} else {
		    ctrl.fields[i].show = false;
		}
	    }

	});
	
	ctrl.experiments = Experiment.query();
	
    });
