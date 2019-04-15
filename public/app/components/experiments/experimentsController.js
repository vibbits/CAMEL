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
	    }
	    ctrl.fields.push(shortRef);
	});


	ctrl.filterBlocks = []
	ctrl.addFilterItem = function(field){
	    ctrl.filterBlocks.push(field);
	}
	ctrl.removeFilterItem = function(filterBlockIndex){
	    ctrl.filterBlocks.splice(filterBlockIndex, 1);
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

	ctrl.filter = {};
	ctrl.query = function(){
	    ctrl.tmp_experiments = Experiment.query(ctrl.filter, function(){
		addShortRefs();
		ctrl.experiments = ctrl.tmp_experiments;
		ctrl.loaded = true;
	    });
	}
	ctrl.loaded = false;
	ctrl.query();
	
    });
