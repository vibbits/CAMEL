var camelApp = angular.module("CAMEL");

camelApp.service('attUpload',['$http',function($http){
    this.uploadFileToUrl = function(file, expId, fieldId, valueId){
	console.log(file);
	url = "/upload/"+expId+'/'+fieldId+'/'+valueId;
        var fd = new FormData();
        fd.append('file', file);
        
        $http.post(url, fd, {
            transformRequest: angular.identity,
            headers: {'Content-Type': undefined}
        });
	    // .success(function() {
	    // 	console.log("upload success");
            // })
	    // .error(function() {
	    // 	console.log("upload error");
            // });
    };
}]);

camelApp.controller('ExpeditController', function($scope, $location, $routeParams, $sce,
						  attUpload, Experiment, Field, Reference){
	var ctrl = this;
	ctrl.fieldsLoaded = false;
	ctrl.refsLoaded = false;
	ctrl.experimentLoaded = false;
	
	ctrl.new_experiment = true;
	
	ctrl.new_incr = 0;
	ctrl.type_map = {}
	
	$scope.guest_email = "";
	$scope.guest_comments = "";

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
	}
	
	$scope.fields = Field.query(function(){
	    ctrl.fieldsLoaded = true;
	    //type mapping
	    for (var i in $scope.fields){
		var field = $scope.fields[i];
		if (field.hasOwnProperty('id')){
		    ctrl.type_map[field.id] = field.type_column.split('_')[1];
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
		    || field_type == 'DOUBLE') {
		    $scope.exp.fields[field_id][new_id] = undefined;
		}
	    }
	};

	/**
	   Checks if there is more than one value left
	   for this field.
	 */
	ctrl.hasFieldValuesLeft = function(field){
	    field_values = $scope.exp.fields[field.id];
	    return Object.keys(field_values).length >1;
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

	ctrl.isValue = function(value){
	    return typeof(value) != 'object';
	};
	
	ctrl.remove_value = function(fieldId, valueId){
	    var field = $scope.exp.fields[fieldId];
	    if (valueId.startsWith("new_")){
		//delete newly created values
		delete field[valueId];
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
	    var $inputField = $('input[name="'+ fieldId+'_'+valueId  +'"]');
	    var files = $inputField[0].files
	    if (files.length == 1){
		attUpload.uploadFileToUrl(files[0], "another problem", fieldId, valueId);
	    }
	} 
    
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
	    $scope.warningMessage = $sce.trustAsHtml("Deleting an experiment cannot be undone. <br><br>"
						     +"Linked references will be removed as well, unless they "
						     +"are still linked to any other experiments.<br><br>"
						     +"Are you sure?");
	    confirmAction = deleteExperiment;
	    $('#confirmModal').modal();
	};
    });
