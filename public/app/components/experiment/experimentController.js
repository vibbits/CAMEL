angular.module("CAMEL")
    .controller('ExperimentController', function($scope, $location, $timeout, $routeParams, $route, $http, Experiment) {
	var ctrl = this;

	ctrl.routeParams = $routeParams;
	ctrl.exp = Experiment.get($routeParams);
    });
