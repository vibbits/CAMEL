angular.module("CAMEL")
    .controller('ExperimentsController', function($scope, $location, $timeout, $routeParams, $route, $http, Experiment, Field) {
	var ctrl = this;

	ctrl.experiments = Experiment.query();
	ctrl.fields = Field.query();
    });
