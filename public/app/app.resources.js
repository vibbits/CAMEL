angular.module("CAMEL")
    .factory("Experiment", function ExperimentFactory($resource, config) {
	return $resource(config.apiUrl+"/experiment/:id", {id: '@id'}, {
	    update: {method: 'PUT'}
	});
    })
    .factory("Field", function FieldFactory($resource, config) {
	return $resource(config.apiUrl+"/field/:id", {id: '@id'}, {
	    update: {method: 'PUT'}
	});
    })
    .factory("Reference", function ReferenceFactory($resource, config) {
	return $resource(config.apiUrl+"/reference/:id", {id: '@id'});
    })
    .factory("Attachment", function AttachmentFactory($resource, config){
	return $resource(config.apiUrl+"/attachment/", {}, {
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
