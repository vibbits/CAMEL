var app = angular.module('CAMEL', ['ngResource','ngRoute']);
app.controller('AppController', function($scope, $rootScope, $location, $route, $document,
					 AUTH_EVENTS, AuthService) {
    
    $scope.auth = AuthService;

    $scope.login = function(){
	AuthService.login().then(function(token){
	    $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
	}, function(){
	    $rootScope.$broadcast(AUTH_EVENTS.loginFailed);
	});
    };
        
    $scope.logout = function(){
	AuthService.logout().then(function(){
	    $rootScope.broadcast(AUTH_EVENTS.logoutSuccess);
	    $location.path('/');
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
