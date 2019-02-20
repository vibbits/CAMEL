angular.module("CAMEL")
    .controller('ExperimentsController', function($scope, $location, $timeout, $routeParams, $route, $http, Experiment, Field) {
	var ctrl = this;

	ctrl.fields = Field.query();	
	ctrl.experiments = Experiment.query();
	
	
	
    });
