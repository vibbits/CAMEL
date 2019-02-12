angular.module("CAMEL")
.factory("Experiment", function ExperimentFactory($resource) {
    return $resource("api/experiment/:id", {id: '@ID'});
});
