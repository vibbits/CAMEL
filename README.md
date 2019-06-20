## CAMEL

This project aims to be an updated, interactive version of:  
https://www.biw.kuleuven.be/comp2/camel/

## Application outline
### Database
MySQL

Schema:

![Database schema overview][db_schema]

The `import_data.py` script starts from the original CAMEL data (xlsx
-> csv), but makes a lot of assumptions about existing fields and
species, so is at the moment NOT suitable as bulk upload script.


[db_schema]: admin/db_overview.png

### Backend

Python3 Flask Restful API

Dependencies:

- flask
- flask_restful
- MySQLdb

Apache webserver needs to have the the `mod_wsgi` module installed for
Python3 with a `ScriptAlias` pointing at the entry point `camel.wsgi`


#### API Calls
All data can be retrieved with simple `get` requests.  
`post`, `put` and `delete` require an `AuthToken` in the headers, as explained below.

Get all experiment data, or one specific experiment.
```
https://dev.bits.vib.be/CAMEL/api/experiment
https://dev.bits.vib.be/CAMEL/api/experiment/<id>
```

The returned JSON is a list of experiments, each with their
attributes, a list of references and a list of fields, indexed by field_id.

The experiment list can be filtered by adding one or more parameters.
```
https://dev.bits.vib.be/CAMEL/api/experiment?<field_id>=<filter>
```
Text fields get searched for the literal string. Numeric fields use a minimum and maximum value instead.

eg. get all experiments where the species contains "phage" and the number of lines is between 12 and 20:
```
https://dev.bits.vib.be/CAMEL/api/experiment?1=phage&min_3=12&max_3=20
```

Get all field data:
```
https://dev.bits.vib.be/CAMEL/api/field
```

Get data for one specific field. Id can be both the field_id or the field title.
```
https://dev.bits.vib.be/CAMEL/api/field/<id>
```

Next to the field properties, the JSON also contains a `values`
attribute, with a list of the values this field contains in the
database, ordered by descending number of occurrences.  This feature
gets extended by adding the `timeline` flag. The values will then be
ordered by year, with the number of occurrences that year.

```
https://dev.bits.vib.be/CAMEL/api/field/<id>?timeline=1
```

A simple list of all references (papers):
```
https://dev.bits.vib.be/CAMEL/api/reference
```

## Authentication

Authentication is done by a separate Flask application.  Visiting the
page served by this app, will return a response containing a
`AuthToken` header. This token is also written to the database. The
page can be secured by setting authentication rules in the `.htaccess`
(Basic Auth, Shiboleth, ...).

The AngularJS application should be including the token in the `AuthToken`
header with every request that should be authenticated by the
API. Tokens get removed from the database after one day, expiring the
session.



### Frontend

AngularJS application with dependencies on Bootstrap MD, JQuery and
eCharts.

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
