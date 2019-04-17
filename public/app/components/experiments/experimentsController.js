angular.module("CAMEL")
    .controller('ExperimentsController', function($scope, $location, $timeout, $routeParams, $route, $http, Experiment, Field) {
	var ctrl = this;
	var showNr = 5;
	
	//extra field for short references
	var shortRef = {
	    'id': 'ref',
	    'title': "Short reference",
	    'type_column': 'value_VARCHAR'	    
	}
	
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
	});


	ctrl.toggleFilterItem = function(field){
	    if (field.filter){
		field.filter = false;
		console.log(ctrl.filter);
		if (field.type_column == 'value_VARCHAR' || field.type_column == 'value_TEXT'){
		    delete ctrl.filter[field.id];
		} else if (field.type_column == 'value_INT'){
		    delete ctrl.filter['min_'+field.id];
		    delete ctrl.filter['max_'+field.id];
		} else if (field.type_column == 'value_DOUBLE'){
		    delete ctrl.filter['dmin_'+field.id];
		    delete ctrl.filter['dmax_'+field.id];
		} else if (field.type_column == 'value_BOOL'){
		    delete ctrl.filter['bool_'+field.id];
		} 
		ctrl.query();
	    } else {
		field.filter = true;
	    }
	}

	
	ctrl.toggleColumn = function(field){
	    field.show = !field.show;
	}
	
	function addShortRefs(){
	    for (var i=0; i<ctrl.tmp_experiments.length; i++){
		longRefs = ctrl.tmp_experiments[i]['references'];
		ctrl.tmp_experiments[i]['fields']['ref'] = [];
		for (var j=0; j<longRefs.length; j++){
		    longRef = longRefs[j];
		    authors = longRef['authors'].split(', ');
		    shortAuthor = authors[0];
		    if (authors.length > 1){
			shortAuthor+=" et al.";
		    }
		    ref = shortAuthor +" ("+longRef['year']+") "+longRef['journal'];
	    	    ctrl.tmp_experiments[i]['fields']['ref'].push(ref);
		}
	    }
	}

	ctrl.filterUpdate = function(filter_id){
	    if (ctrl.filter[filter_id] === ""){
		delete ctrl.filter[filter_id];
	    }
	    ctrl.query();
	}
	
	ctrl.filter = {};
	ctrl.query = function(){
	    ctrl.loaded = false;
	    ctrl.tmp_experiments = Experiment.query(ctrl.filter, function(){
		addShortRefs();
		ctrl.experiments = ctrl.tmp_experiments;
		ctrl.exp_count = ctrl.experiments.length;
		ctrl.loaded = true;
		ctrl.init_loaded = true;
	    });
	}

	//Init query
	ctrl.init_loaded = false;
	ctrl.exp_count = 0;
	ctrl.query();
	
    });
