angular.module("CAMEL").controller('ExpeditController', function($scope, $location, $routeParams, $sce,
								 Experiment, Field, Reference, Attachment, PubMed,
								 config){
    var ctrl = this;
    ctrl.fieldsLoaded = false;
    ctrl.refsLoaded = false;
    ctrl.experimentLoaded = false;
    
    ctrl.new_experiment = true;
    
    ctrl.new_incr = 0;
    ctrl.type_map = {}
    ctrl.req_map = {}
    
    $scope.guest_email = "";
    $scope.guest_comments = "";

    $scope.download_url = config.attachments;
    $scope.attachments = {};
    
    if ($location.$$path.startsWith('/experiment/edit/')
	&& $routeParams.hasOwnProperty('id')){
	ctrl.new_experiment = false;
	$scope.exp = Experiment.get($routeParams, function(){
	    ctrl.experimentLoaded = true;
	},function(){
	    console.log("Unknown experiment id");
	    $location.path('/home');
	});
    } else {
	$scope.exp = new Experiment();	    
	$scope.exp.fields = {};
	$scope.exp.references = [];
	ctrl.experimentLoaded = true;
    }
    
    $scope.fields = Field.query(function(){
	ctrl.fieldsLoaded = true;
	//field mapping
	for (var i in $scope.fields){
	    var field = $scope.fields[i];
	    if (field.hasOwnProperty('id')){
		ctrl.type_map[field.id] = field.type_column.split('_')[1];
		ctrl.req_map[field.id] = field.required;
	    }
	    if (ctrl.new_experiment
		&& field.hasOwnProperty('required') && field['required']){
		$scope.new_field_selected_id = field['id'];
		ctrl.add_field();
	    }
	}
	$scope.new_field_selected_id = undefined;
    });

    $scope.references = Reference.query(function(){
	ctrl.refsLoaded = true;
	ctrl.refPubMedIdMap = {};
	for (var refId in $scope.references){
	    if ($scope.references.hasOwnProperty(refId)){
		var ref = $scope.references[refId];
		if (ref.hasOwnProperty('pubmed_id')){
		    var pubmed_id = ref.pubmed_id;
		    if (pubmed_id){
			ctrl.refPubMedIdMap[pubmed_id] = ref.id;
		    }
		}
	    }
	}
    });


    ctrl.add_field = function(){
	if (!$scope.new_field_selected_id) return;
	
	var new_id = 'new_' + ctrl.new_incr++;
	var field_id = $scope.new_field_selected_id;
	var field_type = ctrl.type_map[field_id];
	if (!$scope.exp.fields.hasOwnProperty(field_id)){
	    $scope.exp.fields[field_id] = {};
	    if (field_type == 'BOOL'){
		$scope.exp.fields[field_id][new_id] = 0;
	    } else {
		$scope.exp.fields[field_id][new_id] = undefined;
	    }
	} else {
	    //don't allow extra values for TEXT and BOOL
	    if (field_type == 'VARCHAR'
		|| field_type == 'INT'
		|| field_type == 'DOUBLE'
		|| field_type == 'ATTACH') {
		$scope.exp.fields[field_id][new_id] = undefined;
	    }
	}
	if (field_type == 'ATTACH'){
	    if (!$scope.attachments.hasOwnProperty(field_id)){
		$scope.attachments[field_id] = {};
	    }
	    $scope.attachments[field_id][new_id] = new Attachment();
	}
    };

    ctrl.pubmed_fill = function(ref){
	var pubmed = PubMed.get({'id': ref.pubmed_id}, function(){
	    ref.title = pubmed.title;
	    ref.authors = pubmed.authors;
	    ref.journal = pubmed.journal;
	    ref.pages = pubmed.pages;
	    ref.url = pubmed.url;
	    if (pubmed.year != null){
		ref.year = pubmed.year;
	    }
	});
    }
    
    ctrl.load_reference = function(){
	if (!$scope.ref_selected_index) return;
	
	var ref_index = $scope.ref_selected_index;
	var add_ref = $scope.references[ref_index];
	var already_loaded = false;
	for (r in $scope.exp.references){
	    var ref = $scope.exp.references[r];		
	    if (ref.hasOwnProperty('id') && ref['id'] == add_ref['id']){
		already_loaded = true;
	    }
	}
	if (!already_loaded){
	    add_ref['action'] = 'loaded';
	    $scope.exp.references.push(add_ref);
	}
    }
    
    ctrl.add_reference = function(){
	var new_ref = {
	    'id': 'new_'+ctrl.new_incr++,
	    'title': '',
	    'authors': '',
	    'journal': '',
	    'year': null,
	    'pages': '',
	    'pubmed_id': null,
	    'url': '',
	    
	    'action': 'new'
	};
	$scope.exp.references.push(new_ref);
    }

    ctrl.isActiveReference = function(ref){
	return !(ref.hasOwnProperty('action') && ref['action'] == 'delete');
    };
    
    ctrl.remove_reference = function(ref){
	if (ref.hasOwnProperty('action') && (ref['action'] == 'new' || ref['action'] == 'loaded')){
	    var ref_index = $scope.exp.references.indexOf(ref);
	    $scope.exp.references.splice(ref_index, 1);	    
	} else {
	    ref['action'] = 'delete';
	}
    };

    /**
     * Is this value a non-action value?
     */
    ctrl.isValue = function(value){
	return typeof(value) != 'object'
	    || value.hasOwnProperty('filename');
    };
    ctrl.isStringValue = function(value){
	return typeof(value) == 'string';
    };
    ctrl.countValues = function(field_id){
	var count=0;
	for (var value_id in $scope.exp.fields[field_id]){
	    if ($scope.exp.fields[field_id].hasOwnProperty(value_id)){
		var value = $scope.exp.fields[field_id][value_id];
		if (value == undefined){
		    count++;
		}
		else if (ctrl.isValue(value)){
		    count++;
		}
	    }
	}
	return count;
    }
    
    /**
     * Does this field have (non-action) values for this experiment?
     * New values will be 'undefined'.
     * Make an exception for just uploaded files.
     */
    ctrl.hasValues = function(field){
	if (!ctrl.experimentLoaded){
	    return false;
	}
	if (!$scope.exp.fields.hasOwnProperty(field.id)){
	    return false;
	}

	var value_count = ctrl.countValues(field.id);
	
	return value_count>0;
    }

    /**
       Checks if there is more than one value left
       for this field.
    */
    ctrl.hasFieldValuesLeft = function(field){
	return ctrl.countValues(field.id) >1;
    }

    /**
     * Always show a close button for attachments fields,
     * except for a last upload control when the field is required.
     */
    ctrl.showRemoveAttachButton = function(field, field_value){
	if (field.required && !ctrl.hasFieldValuesLeft(field)){
	    return !!field_value;
	}
	return true;
    };

    /**
     * Remove a field from the page. New fields will simply be removed,
     * persistent fields will become invisible and get a 'delete' action flag 
     * for the API call.
     * 
     * Removing a required attachment should spawn a new attachment upload control.
     */
    ctrl.remove_value = function(fieldId, valueId){
	var field = $scope.exp.fields[fieldId];
	var field_type = ctrl.type_map[fieldId];	
	if (valueId.startsWith("new_")){
	    //delete newly created values
	    delete field[valueId];
	    if (field_type == 'ATTACH'){
		delete $scope.attachments[fieldId][valueId];
	    }
	} else {
	    //mark existing values as to be deleted
	    field[valueId] = {'action': 'delete'};
	}
	//count remaining value pairs
	var count = 0;
	for (var k in field){
	    if (field.hasOwnProperty(k)){
		count++;
	    }
	}	    
	//remove 'empty' field
	if (count === 0){		
	    delete $scope.exp.fields[fieldId];
	}

	//spawn required ATTACH field
	if (field_type == 'ATTACH' && ctrl.req_map[fieldId]){
	    if (ctrl.countValues(fieldId) == 0){
		$scope.new_field_selected_id = fieldId;
		ctrl.add_field();
	    }
	}
    }

    
    ctrl.submit_changes = function(){
	$scope.nameForm.$submitted = true;
	$scope.fieldsForm.$submitted = true;
	$scope.refForm.$submitted = true;
	if ($scope.nameForm.$invalid
	    || $scope.fieldsForm.$invalid
	    || $scope.refForm.$invalid){
	    return;
	}

	//check for non-uploaded attachments
	var non_uploads = 0;
	for (var f in $scope.attachments){
	    if ($scope.attachments.hasOwnProperty(f)){
		for (var att in $scope.attachments[f]){
		    if ($scope.attachments[f].hasOwnProperty(att)){
			var value = $scope.exp.fields[f][att];
			if (value == undefined){
			    non_uploads++;
			}
		    }
		}
	    }
	}
	if (non_uploads > 0){
	    console.log("Non-uploads pending");
	    return;
	}

	
	if (ctrl.new_experiment){
	    $scope.exp.$save().then(function(){
		$location.path('/experiment/'+$scope.exp.id);
	    });
	} else {
	    $scope.exp.$update().then(function(){
		$location.path('/experiment/'+$scope.exp.id);
	    });
	}
    };
    
    ctrl.uploadAttachment = function(fieldId, valueId){
	var att = $scope.attachments[fieldId][valueId];
	var filename = att.file[0].name;
	att.$save().then(function(){
	    uuid = att.uuid;
	    $scope.exp.fields[fieldId][valueId] = {'filename': filename, 'uuid': uuid};
	});
    };
    
    ctrl.cancel = function(){
	if (ctrl.new_experiment){
	    $location.path('/experiments');
	} else {
	    $location.path('/experiment/'+$scope.exp.id);
	}
    };

    function deleteExperiment(){
	$('#confirmModal').on('hidden.bs.modal', function(e){
	    $scope.$apply(function() {
		$location.path('/experiments');		
	    });
	});	    
	$scope.exp.$delete();	    
    }
    
    var confirmAction;
    $scope.warningTitle = "Warning";
    $scope.warningMessage = "Careful there";
    
    ctrl.confirm = function(confirmData){
	confirmAction(confirmData);
	$('#confirmModal').modal('hide');
    }
    
    ctrl.delete = function(){
	$scope.warningTitle = "Delete Experiment";
	$scope.warningMessage = $sce.trustAsHtml("Deleting an experiment cannot be undone. "
						 +"All data, including uploaded attachments will be removed.<br><br>"
						 +"Linked references will be removed as well, unless they "
						 +"are still linked to any other experiments.<br><br>"
						 +"Are you sure?");
	confirmAction = deleteExperiment;
	$('#confirmModal').modal();
    };
});
