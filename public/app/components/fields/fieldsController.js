angular.module("CAMEL")
    .controller('FieldsController', function($scope, Field){
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
		group: 0,
		group_id: null
	    };
	    ctrl.fields.push(newField);
	};

	ctrl.removeRow = function(field){
	    var doublecheck = false;
	    if (field.hasOwnProperty('id')){	
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
	};

	ctrl.saveChanges = function(){
	    for (f in ctrl.fields){
		field = ctrl.fields[f];
		if (field.changed){
		    console.log(field);
		    field.$update();
		    console.log(field);
		}
	    }
	}
    });
