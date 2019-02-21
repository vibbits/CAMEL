angular.module("CAMEL")
    .controller('ExperimentController', function($scope, $location, $timeout, $routeParams, $route, $http, Experiment, Field) {
		
	$scope.exp = Experiment.get($routeParams);
	$scope.fields = Field.query();
    });
