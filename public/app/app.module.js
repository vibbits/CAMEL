var app = angular.module('CAMEL', ['ngResource','ngRoute']);
app.controller('AppController', function($scope, $location, $route, $document) {
});

app.factory('State', function(){
    return {
	expFilter: {},
	expFields: [],
	expOrder: {},
	expRefs: {}
    }
});
