angular.module("CAMEL")
.factory("Experiment", function ExperimentFactory($resource) {
    return $resource("api/experiment/:id", {id: '@id'}, {
	update: {method: 'PUT'}
    });
})
.factory("Field", function FieldFactory($resource) {
    return $resource("api/field/:id", {id: '@id'}, {
	update: {method: 'PUT'}
    });
})
.factory("Reference", function ReferenceFactory($resource) {
    return $resource("api/reference/:id", {id: '@id'});
});
