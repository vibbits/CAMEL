angular.module("CAMEL")
    .directive('experimentsTable', function($location, State) {
    return {
        restrict: 'E',
        templateUrl: 'app/shared/experimentsTable/experimentsTable.html',
        scope: {
            experiments: '=',
	    fields: '=',
	    refs: '='
        },
	link: function(scope, elem, attr) {
	    scope.showExperiment = function(experiment) {
		$location.path("/experiment/"+experiment.id);
	    };

	    
	    if (!State.expOrder.hasOwnProperty('key')){
		scope.orderParams = {};
		scope.orderParams.key = '';
		scope.orderParams.realm = 'exp';
		scope.orderParams.type = '';
		scope.orderParams.desc = false;
		State.expOrder = scope.orderParams;
	    } else {
		scope.orderParams = State.expOrder;
	    }

	    scope.sortExperiments = function(key, keyRealm='exp'){
		scope.orderParams.realm=keyRealm;
		if (keyRealm == 'fields'){
		    scope.orderParams.type = key.type_column;
		    key = key.id;
		}
		if (keyRealm == 'refs'){
		    key = key.field;
		}
		if (scope.orderParams.key != key){
		    scope.orderParams.key = key;
		    scope.orderParams.desc = false;
		} else {
		    if (!scope.orderParams.desc){
			scope.orderParams.desc = true;
		    } else {
			scope.orderParams.key = '';
			scope.orderParams.desc = false;
		    }		    
		}
	    }
	    var count=0;
	    //orderBy experiments
	    scope.fieldComparator = function(exp1, exp2){
		//both experiments should be objects. if not, keep their natural order.
		if (!scope.orderParams.key || exp1.type !== 'object' || exp2.type !== 'object'){
		    return (exp1.index < exp2.index) ? -1 : 1;
		}

		//order by direct experiment fields
		if (scope.orderParams.realm=='exp'){
		    return (exp1.value[scope.orderParams.key].toLowerCase() < exp2.value[scope.orderParams.key].toLowerCase())? -1:1;
		}

		//order by reference fields
		if (scope.orderParams.realm=='refs'){
		    field1 = exp1.value.references[0][scope.orderParams.key];
		    field2 = exp2.value.references[0][scope.orderParams.key];
		    return (field1 < field2)? -1:1;
		}

		if (scope.orderParams.realm=='fields'){
		    //order by dynamic fields

		    //non-existent fields are at the end of the list
		    //existing fields are arrays: order by the first item
		    if (exp1.value.fields.hasOwnProperty(scope.orderParams.key)){
			field1 = exp1.value.fields[scope.orderParams.key][0];
			if (scope.orderParams.type == 'value_VARCHAR' || scope.orderParams.type == 'value_TEXT'){
			    field1 = field1.toString().toLowerCase();
			}
		    } else {
			return 1;
		    }
		    if (exp2.value.fields.hasOwnProperty(scope.orderParams.key)){
			field2 = exp2.value.fields[scope.orderParams.key][0];
			if (scope.orderParams.type == 'value_VARCHAR' || scope.orderParams.type == 'value_TEXT'){
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
