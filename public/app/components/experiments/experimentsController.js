angular.module("CAMEL")
    .controller('ExperimentsController', function($scope, $location, $timeout, $routeParams, $route, $http, Experiment) {
	var ctrl = this;

	ctrl.experiments = Experiment.query();
    });
