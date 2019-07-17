angular.module('CAMEL')
    .config(['$routeProvider', function($routeProvider) {
	$routeProvider
	    .when('/home', {
		templateUrl:  'app/components/home/homeTemplate.html',
		controller: 'HomeController',
		controllerAs: 'home'
	    })
	    .when('/contact', {
		templateUrl:  'app/components/contact/contactTemplate.html',
		controller: 'ContactController',
		controllerAs: 'contact'
	    })
	    .when('/info', {
		templateUrl:  'app/components/info/infoTemplate.html',
		controller: 'InfoController',
		controllerAs: 'info'
	    })
	    .when('/experiment/add', {
		templateUrl:  'app/components/expedit/expeditTemplate.html',
		controller: 'ExpeditController',
		controllerAs: 'expedit',
		data: {'protected': true}
	    })
	    .when('/experiment/edit/:id', {
		templateUrl:  'app/components/expedit/expeditTemplate.html',
		controller: 'ExpeditController',
		controllerAs: 'expedit',
		data: {'protected': true}
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
    .run(function($rootScope, $location, $window, AUTH_EVENTS, AuthService){
	// initialise google analytics
	$window.ga('create', 'UA-134601105-1', 'auto');
	// track pageview on state change
	$rootScope.$on('$locationChangeStart', function (event) {
            $window.ga('send', 'pageview', $location.path());
	});
	
	$rootScope.$on('$routeChangeStart', function(event, next){
            if (next.hasOwnProperty('$$route') && next.$$route.hasOwnProperty('data') && next.$$route.data.hasOwnProperty('protected')){
		var protected = next.$$route.data.protected;
		if (protected && !AuthService.isAuthenticated()){
                    event.preventDefault();
                    $rootScope.$broadcast(AUTH_EVENTS.notAuthenticated, next);
		}
            }
	});	
	$rootScope.$on(AUTH_EVENTS.notAuthenticated, function(event, next){
	    console.log("Not Authenticated Event");
	    $location.path('/');
	    AuthService.login().then(function(token){
		$rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
		$location.path(next.$$route.originalPath);
	    }, function(){
		$rootScope.$broadcast(AUTH_EVENTS.loginFailed);
	    });
	});	
    });
