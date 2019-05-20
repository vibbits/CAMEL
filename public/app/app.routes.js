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
    .when('/experiments', {
		templateUrl:  'app/components/experiments/experimentsTemplate.html',
		controller: 'ExperimentsController',
		controllerAs: 'experiments'
	})
    .when('/fields', {
		templateUrl:  'app/components/fields/fieldsTemplate.html',
		controller: 'FieldsController',
		controllerAs: 'fields',
        data: {'protected': true}
	})
    .otherwise({
		redirectTo: '/home'
	});
}])
.run(function($rootScope, AUTH_EVENTS, AuthService){
    $rootScope.$on('$routeChangeStart', function(event, next){
        if (next.$$route.hasOwnProperty('data') && next.$$route.data.hasOwnProperty('protected')){
            var protected = next.$$route.data.protected;
            if (protected && !AuthService.isAuthenticated()){
                event.preventDefault();
                $rootScope.$broadcast(AUTH_EVENTS.notAuthenticated);
            }
        }
    });
});
