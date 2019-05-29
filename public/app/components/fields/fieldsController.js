angular.module("CAMEL")
    .controller('FieldsController', function($scope, Field, State){
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

	ctrl.removeRow = function(field){
	    var doublecheck = false;
	    if (!field.new_field){
		//deleting an existing field causes all data
		//to be removed!
		alert("Are you sure?");
		double_check = true;
		if (double_check){
		    field.$delete();
		} else {
		    return;
		}
	    } 
	    var index = ctrl.fields.indexOf(field);
	    if (index !== -1){
		ctrl.fields.splice(index, 1);
	    }
	    State.refresh();
	};

	ctrl.saveChanges = function(){
	    for (f in ctrl.fields){
		field = ctrl.fields[f];
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
	};
    });
