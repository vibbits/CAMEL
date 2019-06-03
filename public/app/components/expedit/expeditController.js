angular.module("CAMEL")
    .controller('ExpeditController', function($scope, $routeParams, Experiment, Field){
	var ctrl = this;
	ctrl.fieldsLoaded = false;
	ctrl.experimentLoaded = false;
	
	$scope.fields = Field.query(function(){
	    ctrl.fieldsLoaded = true;
	});

	$scope.exp = Experiment.get($routeParams, function(){
	    ctrl.experimentLoaded = true;
	});	
    });
