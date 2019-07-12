// Copy this file to `app.config.js` and replace the
// URLs with the correct hosting locations.
angular.module("camel.constants", [])
    .constant('config', {
	apiUrl: "http://localhost/CAMEL/api",
	attachments: "http://localhost/camel_files"	
    });
