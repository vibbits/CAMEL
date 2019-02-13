angular.module("CAMEL")
.directive('experimentsTable', function($location) {
    return {
        restrict: 'E',
        templateUrl: 'app/shared/experimentsTable/experimentsTable.html',
        scope: {
            experiments: '='
        }
    };
});
