angular.module('CAMEL')
.config(['$routeProvider', function($routeProvider) {
	$routeProvider
	.when('/home', {
		templateUrl:  'app/components/home/homeTemplate.html',
		controller: 'HomeController',
		controllerAs: 'home'
	})
    	.when('/experiment/:id', {
		templateUrl:  'app/components/experiment/experimentTemplate.html',
		controller: 'ExperimentController',
		controllerAs: 'experiment'
	})
    	.otherwise({
		redirectTo: '/home'
	});;
}]);
