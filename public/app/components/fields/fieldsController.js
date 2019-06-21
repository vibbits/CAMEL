angular.module("CAMEL")
    .controller('FieldsController', function($scope, $location, $sce, Field, State){
	var ctrl = this;
	ctrl.loaded = false;
	
	ctrl.fields = Field.query(function(){
	    ctrl.loaded = true;
	});
	
	ctrl.newRow = function(){
	    var newField = {
		title: '',
		unit: '',
		description: '',
		type_column: 'value_VARCHAR',
		link: 0,
		required: 0,
		weight: 9000,
		group: 0,
		group_id: null,
		new_field: true
	    };
	    ctrl.fields.push(newField);
	};

	
	function deleteRow(field){
	    if (!field.new_field){		
		field.$delete();
	    }

	    var toDelete = [field];
	    //remove dependent fields
	    if (field.group){
		var gid = field.id;
		for (var f in ctrl.fields){
		    var subField = ctrl.fields[f];
		    if (subField.hasOwnProperty('group_id')){
			if(subField.group_id == gid){
			    toDelete.push(subField);
			}
		    }		    
		}
	    }

	    for (var f in toDelete){
		var delField = toDelete[f];
		var index = ctrl.fields.indexOf(delField);
		if (index !== -1){
		    ctrl.fields.splice(index, 1);
		}
	    }
	    
	    State.refresh();
	}
	
	function changeColType(){
	    console.log("Change col type");
	}

	var confirmAction;
	$scope.warningTitle = "Warning";
	$scope.warningMessage = "Careful there";
	
	ctrl.confirm = function(confirmData){
	    confirmAction(confirmData);
	    $('#confirmModal').modal('hide');
	}
	
	ctrl.removeRow = function(field){
	    if (!field.new_field){
		$scope.warningTitle = "Delete field";
		var warningMessage = "Deleting a field cannot be undone. <br>"
		    + " If this field contains data for any experiments, this data will be lost.";
		if (field.group){
		    warningMessage+="<br><br>"
			+"This field is labeled as a group field, which means all "
			+"dependent fields will also be deleted together with their data.";
		}
		$scope.warningMessage = $sce.trustAsHtml(warningMessage);
		$scope.confirmData = field;
		confirmAction = deleteRow;
		$('#confirmModal').modal();		
	    } else {
		deleteRow(field);
	    }
	};

	ctrl.saveChanges = function(){
	    $scope.fieldUpdateForm.$submitted = true;
	    if($scope.fieldUpdateForm.$invalid){
		return;
	    }
	    
	    for (var f in ctrl.fields){
		var field = ctrl.fields[f];
		if (field.new_field){
		    newField = new Field(field);
		    ctrl.fields[f] = newField;
		    newField.$save();
		} else if (field.changed){
		    field.$update();
		    field.changed = false;
		}
	    }
	    //Force the ExperimentsController to reload the fields
	    State.refresh();
	    $scope.fieldUpdateForm.$submitted = false;
	    $scope.fieldUpdateForm.$pristine = true;
	};

	ctrl.cancel = function(){
	    $location.path('home');
	}
	
    });
