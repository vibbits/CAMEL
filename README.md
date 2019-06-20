## CAMEL

This project aims to be an updated, interactive version of:  
https://www.biw.kuleuven.be/comp2/camel/

## Application outline
### Database
MySQL

Schema: `admin/dbschema.sql`

![Database scheme overview][db_scheme]

The `import_data.py` script starts from the original CAMEL data (xlsx
-> csv), but makes a lot of assumptions about existing fields and
species, so is at the moment NOT suitable as bulk upload script.


[db_scheme]: admin/db_overview.png

### Backend

Python3 Flask Restful API

Dependencies:

- flask
- flask_restful
- MySQLdb

Apache webserver needs to have the the `mod_wsgi` module installed for
Python3 with a `ScriptAlias` pointing at the entry point `camel.wsgi`

### Frontend

AngularJS application with dependencies on Bootstrap MD, JQuery and eCharts.

Apache should use `public` as the DocumentRoot for this application.

#### Versions and API's
 * AngularJS 1.7.6  
   https://code.angularjs.org/1.7.6/docs/guide
 * JQuery 3.3.1  
   https://api.jquery.com/
 * Popper.js 1.15  
   https://popper.js.org/
 * Bootstrap Material Design 4.0.0  
   https://fezvrasta.github.io/bootstrap-material-design/docs/4.0/getting-started/introduction/
 * eCharts 4.2.1  
   https://echarts.apache.org/en/api.html#echarts

## Hosting
The development version can be viewed at
https://dev.bits.vib.be/CAMEL/

## Authentication

Currently authentication is done by a separate Flask application.
Visiting the page served by this app, will return a response
containing a `AuthToken` header. This token is also written to the
database. The page can be secured by setting authentication rules in
the `.htaccess` (Basic Auth, Shiboleth, ...).

The AngularJS application should be including the token in the `AuthToken`
header with every request that should be authenticated by the
API. Tokens get removed from the database after one day, expiring the
session.
