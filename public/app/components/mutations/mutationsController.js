angular.module("CAMEL")
    .controller('MutationsController', function($scope, $location, $window, $timeout, $routeParams, $route, $http, Mutation, Field, State){
	var ctrl = this;
    var showNr = 1;
    ctrl.refs = State.expRefs;

    ctrl.toggleRefShow = function(ref){
	    ref.show = !ref.show;
	}
	ctrl.toggleRefFilter = function(ref){
	    ref.filter = !ref.filter;
	}

    //Init fields
    if (State.expFields.length == 0){
	    ctrl.fields = Field.query(function(){
		var i = 0;
		for (var field_i in ctrl.fields){
		    if (ctrl.fields.hasOwnProperty(field_i)){
			var field = ctrl.fields[field_i];
			if (i<showNr || (i>37 && i<44)){
			    field.show = true;
			} else {
			    field.show = false;
			}
			field.filter = false;
			if (field.type_column == 'value_VARCHAR' && field.options){
			    field.options = field.options.split(/ *, */);
			}
			i++;
		    }
		}
		State.expFields = ctrl.fields;
	    });
	} else {
	    ctrl.fields = State.expFields;
	}

	ctrl.toggleFilterItem = function(field){
	    if (field.filter){
		field.filter = false;
		if (field.hasOwnProperty('type_column')){
		    switch(field.type_column){
		    case 'value_VARCHAR':
		    case 'value_TEXT':
		    case 'value_BOOL':
		    case 'value_ATTACH':
			delete ctrl.filter[field.id];
			break;
		    case 'value_INT':
		    case 'value_DOUBLE':
			delete ctrl.filter['min_'+field.id];
			delete ctrl.filter['max_'+field.id];
			break;
		    }
		} else{
		    if (field.field == 'year'){
			delete ctrl.filter['ref_min_year'];
			delete ctrl.filter['ref_max_year'];
		    } else {
			delete ctrl.filter['ref_'+field.field];
		    }
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
	    ctrl.tmp_experiments = Mutation.query(ctrl.filter, function(){
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
	ctrl.experiments = [];
	ctrl.query();

	ctrl.export = function(){
	    filter_params = $.param(ctrl.filter);
	    export_url = "api/export";
	    if (filter_params != ''){
		export_url+='?';
		export_url+=filter_params;
	    }
	    $window.location.href = export_url;
	};

    });
