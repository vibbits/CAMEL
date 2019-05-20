var app = angular.module('CAMEL', ['ngResource','ngRoute']);
app.controller('AppController', function($scope, $rootScope, $location, $route, $document,
					 AUTH_EVENTS, AuthService) {
    
    $scope.loginToken = null;
    $scope.setLoginToken = function(token){
	$scope.loginToken = token;
    }
    
    $scope.login = function(){
	AuthService.login().then(function(token){
	    $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
	    $scope.setLoginToken(token);
	}, function(){
	    $rootScope.$broadcast(AUTH_EVENTS.loginFailed);
	});
    };

    $scope.logout = function(){
	AuthService.logout();
	$location.path('/');
	$scope.loginToken = null;
    }
    
});

app.factory('State', function(){
    return {
	expFilter: {},
	expFields: [],
	expOrder: {},
	expRefs: {}
    }
});
