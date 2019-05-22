angular.module("CAMEL")
    .controller('FieldsController', function($scope, Field){
	var ctrl = this;
	ctrl.loaded = false;
	
	ctrl.fields = Field.query(function(){
	    ctrl.loaded = true;
	});
	
    });
