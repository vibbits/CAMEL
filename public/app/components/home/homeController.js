angular.module("CAMEL")
.controller('HomeController', function($location, $routeParams, $route, Experiment) {
    var ctrl = this;

    ctrl.experiments = Experiment.query();
});
