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
	    if (!field.hasOwnProperty('id')){
		//new fields can simply be removed
		var index = ctrl.fields.indexOf(field);
		if (index !== -1){
		    ctrl.fields.splice(index, 1);
		}
	    } else {
		//deleting an existing field causes all data
		//to be removed!
		alert("Are you sure?");
		
	    }
	}
    });
