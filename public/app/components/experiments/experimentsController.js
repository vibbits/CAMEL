angular.module("CAMEL")
    .controller('ExperimentsController', function($scope, $location, $window, $timeout, $routeParams, $route, $http, Experiment, Field, State) {
	var ctrl = this;
	var showNr = 5;

	if (!State.expRefs.hasOwnProperty('authors')){	    
	    ctrl.refs = {
		authors: {
		    header: 'Authors',
		    field: 'authors',
		    show: false,
		    filter: false
		},
		title: {
		    header: 'Pub. Title',
		    field: 'title',
		    show: false,
		    filter: false
		},	    
		year: {
		    header: 'Year',
		    field: 'year',
		    show: false,
		    filter: false
		},
		journal: {
		    header: 'Journal',
		    field: 'journal',
		    show: false,
		    filter: false
		},
		pubmed_id: {
		    header: 'Pubmed ID',
		    field: 'pubmed_id',
		    show: false,
		    filter: false
		}
	    }
	    State.expRefs = ctrl.refs;
	} else {
	    ctrl.refs = State.expRefs;
	}

	ctrl.toggleRefShow = function(ref){
	    ref.show = !ref.show;
	}
	ctrl.toggleRefFilter = function(ref){
	    ref.filter = !ref.filter;
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
