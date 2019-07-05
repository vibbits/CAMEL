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
})
.factory("Attachment", function AttachmentFactory($resource){
    return $resource("api/attachment/", {}, {
	save: {
	    method: 'POST',
	    transformRequest: function(data) {
		if (data === undefined)
		    return data;

		var fd = new FormData();
		angular.forEach(data, function(value, key) {
		    if (value instanceof FileList) {
			if (value.length == 1) {
			    fd.append(key, value[0]);
			} else {
			    angular.forEach(value, function(file, index) {
				fd.append(key + '_' + index, file);
			    });
			}
		    } else {
			fd.append(key, value);
		    }
		});
		return fd;
	    },
	    headers: {
		'Content-Type': undefined
	    }
	}
    });
});
