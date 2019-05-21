angular.module('CAMEL')
    .factory('AuthService', function ($http, Session){
	var authService = {};
	
	authService.login = function(){
	    return $http
		.head('auth')
		.then(function(res){
		    token = res.headers('Authorization');
		    Session.create(token);
		    return token;
		});
	};

	authService.logout = function(){
	    return $http
		.head('auth/logout')
		.then(function(res){
		    Session.destroy();		    
		});
	};
	
	authService.isAuthenticated = function(){
	    return !!Session.token;
	};
		
	return authService;
    })

    .service('Session', function(){
	this.create = function (sessionToken){
	    this.token = sessionToken;
	};
	this.destroy = function(){
	    this.token = null;
	};
    })

    .constant('AUTH_EVENTS', {
	loginSuccess: 'auth-login-success',
	loginFailed: 'auth-login-failed',
	logoutSuccess: 'auth-logout-success',
	sessionTimeout: 'auth-session-timeout',
	notAuthenticated: 'auth-not-authenticated',
	notAuthorized: 'auth-not-authorized'
    });
