angular.module("CAMEL")
    .controller('ExperimentsController', function($scope, $location, $timeout, $routeParams, $route, $http, Experiment, Field, State) {
	var ctrl = this;
	var showNr = 5;

	ctrl.showReferences = false;
	ctrl.toggleShowReferences = function(){
	    ctrl.showReferences = !ctrl.showReferences;
	}
	
	//Init fields
	if (State.expFields.length == 0){
	    ctrl.fields = Field.query(function(){
		for (var i=0; i<ctrl.fields.length; i++){
		    if (i<showNr){
			ctrl.fields[i].show = true;
		    } else {
			ctrl.fields[i].show = false;
		    }
		    ctrl.fields[i].filter = false;
		}
		ctrl.fields.push(shortRef);
		State.expFields = ctrl.fields;
	    });
	} else {
	    ctrl.fields = State.expFields;
	}


	ctrl.toggleFilterItem = function(field){
	    if (field.filter){
		field.filter = false;
		switch(field.type_column){
		case 'value_VARCHAR':
		case 'value_TEXT':
		case 'value_BOOL':
		    delete ctrl.filter[field.id];
		    break;
		case 'value_INT':
		case 'value_DOUBLE':
		    delete ctrl.filter['min_'+field.id];
		    delete ctrl.filter['max_'+field.id];
		    break;
		}
		ctrl.query();
	    } else {
		field.filter = true;
	    }
	}

	
	ctrl.toggleColumn = function(field){
	    field.show = !field.show;
	}
	
	ctrl.filterUpdate = function(filter_id){
	    if (ctrl.filter[filter_id] === ""){
		delete ctrl.filter[filter_id];
	    }
	    ctrl.query();
	}


	ctrl.query = function(){
	    ctrl.loaded = false;
	    ctrl.tmp_experiments = Experiment.query(ctrl.filter, function(){
		ctrl.experiments = ctrl.tmp_experiments;
		ctrl.exp_count = ctrl.experiments.length;
		ctrl.loaded = true;
		ctrl.init_loaded = true;
	    });
	}

	//Init query
	ctrl.filter = State.expFilter;
	ctrl.init_loaded = false;
	ctrl.exp_count = 0;
	ctrl.query();
	
    });
