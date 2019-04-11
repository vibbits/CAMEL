angular.module("CAMEL")
    .controller('ExperimentsController', function($scope, $location, $timeout, $routeParams, $route, $http, Experiment, Field) {
	var ctrl = this;
	var showNr = 5;

	//extra field for short references
	var shortRef = {
	    'id': 'ref',
	    'title': "Reference",
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
	
	ctrl.experiments = Experiment.query(function(){
	    for (var i=0; i<ctrl.experiments.length; i++){
		longRefs = ctrl.experiments[i]['references'];
		ctrl.experiments[i]['fields']['ref'] = [];
		for (var j=0; j<longRefs.length; j++){
		    longRef = longRefs[j];
		    authors = longRef['authors'].split(', ');
		    shortAuthor = authors[0];
		    if (authors.length > 1){
			shortAuthor+=" et al.";
		    }
		    ref = shortAuthor +" ("+longRef['year']+") "+longRef['journal'];
	    	    ctrl.experiments[i]['fields']['ref'].push(ref);
		}
	    }
	});	
    });
