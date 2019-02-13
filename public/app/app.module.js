var app = angular.module('CAMEL', ['ngResource','ngRoute']);
app.controller('AppController', function($scope, $location, $route, $document) {

    $scope.navigateTo = function(path, savePath) {
        if (savePath) {
            $location.search("returnUrl", $location.path());
        }
        $route.reload();
        $location.path("/"+path);
        if ($(".navbar-header").css("float") == 'none') {
            $("#contra-navbar-collapse").collapse('toggle');
        }
    }

    $scope.isCurrent = function(path, level) {
        if (!level) level = 1;
        var loc = $location.path().split("/");
        return loc[level] == path;
    }

});
