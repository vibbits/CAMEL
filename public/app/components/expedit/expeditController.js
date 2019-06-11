angular.module("CAMEL")
    .controller('ExpeditController', function($scope, $location, $routeParams, Experiment, Field){
	var ctrl = this;
	ctrl.fieldsLoaded = false;
	ctrl.experimentLoaded = false;
	ctrl.new_experiment = true;
	
	ctrl.new_incr = 0;
	ctrl.type_map = {}
	
	$scope.guest_email = "";
	$scope.guest_comments = "";
	
	$scope.fields = Field.query(function(){
	    ctrl.fieldsLoaded = true;
	    //type mapping
	    for (var i in $scope.fields){
		var field = $scope.fields[i];
		if (field.hasOwnProperty('id')){
		    ctrl.type_map[field.id] = field.type_column.split('_')[1];
		}
	    }
	});

	if ($location.$$path.startsWith('/experiment/edit/')
	    && $routeParams.hasOwnProperty('id')){
	    $scope.exp = Experiment.get($routeParams, function(){
		ctrl.experimentLoaded = true;
		ctrl.new_experiment = false;
	    },function(){
		console.log("Unknown experiment id");
		$location.path('/home');
	    });
	} else {
	    $scope.exp = new Experiment();	    
	    $scope.exp.fields = {};
	    $scope.exp.references = [];
	}

	ctrl.add_field = function(){
	    var new_id = 'new_' + ctrl.new_incr++;
	    var field_id = $scope.new_field_selected_id;
	    var field_type = ctrl.type_map[field_id];
	    if (!$scope.exp.fields.hasOwnProperty(field_id)){
		$scope.exp.fields[field_id] = {};
		$scope.exp.fields[field_id][new_id] = undefined;
	    } else {
		//don't allow extra values for TEXT and BOOL
		if (field_type == 'VARCHAR'
		    || field_type == 'INT'
		    || field_type == 'DOUBLE') {
		    $scope.exp.fields[field_id][new_id] = undefined;
		}
	    }
	};

	ctrl.submit_changes = function(){
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

	ctrl.cancel = function(){
	    if (ctrl.new_experiment){
		$location.path('/experiments');
	    } else {
		$location.path('/experiment/'+$scope.exp.id);
	    }
	};
	
	ctrl.delete = function(){
	    $scope.exp.$delete().then(function(){
		$location.path('/experiments');
	    });
	};
    });
