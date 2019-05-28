angular.module("CAMEL")
.factory("Experiment", function ExperimentFactory($resource) {
    return $resource("api/experiment/:id", {id: '@id'});
})
.factory("Field", function FieldFactory($resource) {
    return $resource("api/field/:id", {id: '@id'});
});
