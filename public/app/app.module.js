var app = angular.module('CAMEL', ['ngResource','ngRoute', 'ngSanitize']);
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
	    $rootScope.$broadcast(AUTH_EVENTS.logoutSuccess);
	    $location.path('/');
	});
    };

    $scope.navigateTo = function(page){
	$location.path(page);
    };

    $scope.isCurrent = function(path){
	var loc = $location.path().split("/");
        return loc[1] == path;
    }
});

app.factory('State', function(){
    return {
	//experiment filters
	expFilter: {},
	
	//list of experiment fields
	expFields: [],
	
	//current order column/direction/realm
	expOrder: {},
	
	//'extra' fields for references
	expRefs: {},

	//paging
	paging: {currentPage: 1},
	
	refresh: function(){
	    this.expFilter = {};
	    this.expFields = [];
	    this.expOrder = {};
	    this.expRefs = {};
	    this.paging = {currentPage: 1};
	}
    }
});
