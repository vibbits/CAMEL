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
	    scope.keyRealm = 'exp';
	    scope.keyType = '';
	    scope.orderDesc = false;
	    scope.sortExperiments = function(key, keyRealm='exp'){
		scope.keyRealm=keyRealm;
		if (keyRealm == 'fields'){
		    scope.keyType = key.type_column;
		    key = key.id;
		}
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
	    var count=0;
	    //orderBy experiments
	    scope.fieldComparator = function(exp1, exp2){
		//both experiments should be objects. if not, keep their natural order.
		if (!scope.orderKey || exp1.type !== 'object' || exp2.type !== 'object'){
		    return (exp1.index < exp2.index) ? -1 : 1;
		}

		//order by direct experiment fields
		if (scope.keyRealm=='exp'){
		    return (exp1.value[scope.orderKey].toLowerCase() < exp2.value[scope.orderKey].toLowerCase())? -1:1;
		}

		//order by reference fields
		if (scope.keyRealm=='ref'){
		    //TODO
		}

		if (scope.keyRealm=='fields'){
		    //order by dynamic fields

		    //non-existent fields are at the end of the list
		    //existing fields are arrays: order by the first item
		    if (exp1.value.fields.hasOwnProperty(scope.orderKey)){
			field1 = exp1.value.fields[scope.orderKey][0];
			if (scope.keyType == 'value_VARCHAR' || scope.keyType == 'value_TEXT'){
			    field1 = field1.toString().toLowerCase();
			}
		    } else {
			return 1;
		    }
		    if (exp2.value.fields.hasOwnProperty(scope.orderKey)){
			field2 = exp2.value.fields[scope.orderKey][0];
			if (scope.keyType == 'value_VARCHAR' || scope.keyType == 'value_TEXT'){
			    field2 = field2.toString().toLowerCase();
			}
		    } else {
			return -1;
		    }

		    //compare given fields
		    return (field1 < field2)? -1:1;
		}
	    }
        }
    };
});
