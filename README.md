## CAMEL

This project aims to be an updated, interactive version of:  
https://www.biw.kuleuven.be/comp2/camel/

## Application outline
### Database
MySQL

Schema: `admin/dbschema.sql`

The `import_data.py` script starts from the original CAMEL data (xlsx
-> csv), but makes a lot of assumptions about existing fields and
species, so is at the moment NOT suitable as bulk upload script.

### Backend

Python3 Flask Restful API

Dependencies:

- flask
- flask_restful
- MySQLdb

Apache webserver needs to have the the `mod_wsgi` module installed for
Python3 with a `ScriptAlias` pointing at the entry point `camel.wsgi`

### Frontend

AngularJS application with dependencies on Bootstrap, JQuery and eCharts.

Apache should use `public` as the DocumentRoot for this application.

## Hosting
The development version can be viewed at
https://dev.bits.vib.be/CAMEL/

