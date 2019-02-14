angular.module("CAMEL")
.directive('experimentsTable', function($location) {
    return {
        restrict: 'E',
        templateUrl: 'app/shared/experimentsTable/experimentsTable.html',
        scope: {
            experiments: '='
        },
	link: function(scope, elem, attr) {
	    scope.showExperiment = function(experiment) {
		$location.path("/experiment/"+experiment.id);
	    }
        }
    };
});
