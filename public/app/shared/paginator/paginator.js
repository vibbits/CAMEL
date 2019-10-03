angular.module("CAMEL")
    .directive('paginator', function($location, State, config) {
    return {
        restrict: 'E',
        templateUrl: 'app/shared/paginator/paginator.html',
        scope: {
            paging: '=',
	    itemsPerPage: '=',
	    experiments: '='
        },
	link: function(scope, elem, attr) {

	    scope.$watch('experiments.length', function(newValue, oldValue, scope){
		scope.totalItems = scope.experiments.length;
		scope.numPages = Math.ceil(scope.totalItems / scope.itemsPerPage);
		if (scope.numPages != 0){
		    scope.paging.currentPage = Math.min(scope.paging.currentPage, scope.numPages);
		}
	    });

	    
	    scope.firstPage = function(){
		scope.paging.currentPage = 1;
	    };
	    scope.prevPage = function(){
		if (scope.paging.currentPage > 1){		    
		    scope.paging.currentPage -=1;
		}
	    };
	    scope.nextPage = function(){
		if (scope.paging.currentPage < scope.numPages){		    
		    scope.paging.currentPage +=1;
		}
	    };	    
	    scope.lastPage = function(){
		scope.paging.currentPage = scope.numPages;
	    };	    
	}
    }
    });
