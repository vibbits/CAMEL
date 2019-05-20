var app = angular.module('CAMEL', ['ngResource','ngRoute']);
app.controller('AppController', function($scope, $rootScope, $location, $route, $document,
					 AUTH_EVENTS, AuthService) {
    
    $scope.loginToken = null;
    $scope.setLoginToken = function(token){
	//now using the login token as user name
	//might be replaced by actual user information at later point
	$scope.loginToken = token;
    }
    
    $scope.login = function(){
	console.log("Attempting login");
	AuthService.login().then(function(token){
	    $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
	    $scope.setLoginToken(token);
	}, function(){
	    $rootScope.$broadcast(AUTH_EVENTS.loginFailed);
	});
    };
    
    
});

app.factory('State', function(){
    return {
	expFilter: {},
	expFields: [],
	expOrder: {},
	expRefs: {}
    }
});
