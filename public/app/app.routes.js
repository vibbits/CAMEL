angular.module('CAMEL')
.config(['$routeProvider', function($routeProvider) {
	$routeProvider
	.when('/home', {
		templateUrl:  'app/components/home/homeTemplate.html',
		controller: 'HomeController',
		controllerAs: 'home'
	});
}]);
