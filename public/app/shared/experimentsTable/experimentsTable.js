angular.module("CAMEL")
.directive('experimentsTable', function($location) {
    return {
        restrict: 'E',
        templateUrl: 'app/shared/experimentsTable/experimentsTable.html',
        scope: {
            experiments: '=',
	    fields: '='
        },
	link: function(scope, elem, attr) {
	    scope.showExperiment = function(experiment) {
		$location.path("/experiment/"+experiment.id);
	    };
	    scope.orderKey = '';
	    scope.orderDesc = false;
	    scope.sortExperiments = function(key){
		if (scope.orderKey != key){
		    scope.orderKey = key;
		    scope.orderDesc = false;
		} else {
		    if (!scope.orderDesc){
			scope.orderDesc = true;
		    } else {
			scope.orderKey = '';
			scope.orderDesc = false;
		    }		    
		}
	    }
	    scope.fieldComparator = function(exp1, exp2){
		if (scope.orderKey == 'name'){
		    return (exp1['name'] < exp2['name'])? -1:-1;
		}
	    }
        }
    };
});
