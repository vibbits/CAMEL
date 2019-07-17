angular.module("CAMEL")
    .controller('InfoController', function($scope, $location, config){
	var ctrl = this;

	$scope.config = config;
    });
