
# Flask(-Apache2-wsgi-Python3-Ubuntu) Docker image

Environment set up to run Flask app.

To be more specific, resulting Docker container, created from this image, would have:

- Apache (running web server);

- wsgi configured on Apache;

- python3 and pip3 set up;

- Flask app (set up with wsgi and Apache; and running)

- mariadb


To verify that all works, minimal ***example Flask app***. As ***example Flask app*** does not have much content it could be easily replaced with some other Flask app.


This project could be used, for example:

- as a base for (or for bootstrapping) Flask project that require similar characteristics (i.e., starting fresh project from beginning);

- as additional learning material when learning Docker.


## Running (from code)

### Test run

To verify that it works.

1. Clone the project.

2. `cd docker-flask-app-apache2-wsgi-py3-mariadb`

3. `docker-compose build` (or with env variables - see comments in Dockerfile under 'To get following env arguments filled')

4. `docker-compose up -d`

5. Verify. In browser, open: http://localhost:8888/api/hello. The webpage (of ***example Flask app***) should appear.

6. `docker-compose down`


### When using this project as a basis upon to build your own Flask web app


1. Clone the project.

2. Create a folder for your new project.

3. `cd <your project>`

4. Copy contents of cloned project to your project folder. 
   Introduce your code/edits. 
   For example, you might consider updating requirements.txt (you might require different set of Python packages in your app; example on how to update: `pip3 freeze > requirements.txt`), docker-compose.yml.
   
   Depending on the python packages needed in your app some changes to the Dockerfile could be necessary (e.g. missing system library dependencies).
   
   Importantly, some changes to the Dockerfile could be necessary if you like to have another name of the root folder for Apache.
   see lines 7, 8, 26, 34, 39
   You also need a configuration file for Apache which defines a `ScriptAlias` which points to `camel.wsgi`, currently, this
   is CAMELApache.conf
   
   Currently, the setup assumes to expose the API <root folder>/api. A local user `camel` is the owner of the folders as well as the
   user in the database.

	```
	<VirtualHost *:80>

    # ServerName <yourdomainnamehere>

    WSGIDaemonProcess CAMEL user=camel group=www-data threads=5
    WSGIScriptAlias /api /var/www/CAMEL/api/camel.wsgi

    <Directory /var/www/CAMEL/api>
        WSGIProcessGroup CAMEL
        WSGIApplicationGroup %{GLOBAL}
        # For Apache 2.4
        Require all granted
    </Directory>

    ErrorLog /var/www/CAMEL/error.log
    LogLevel debug
    CustomLog /var/www/CAMEL/access.log combined

   </VirtualHost>
   ```
   
   in order to be able to connect to the database, you need a configuration file `camel.conf` with the connection details
   identical to the connection details specified in the environment section of the database service `db` in the `docker-compose.yml` file.
   The host is the name defined in `container-name`.
   ```
    environment:
      MYSQL_ROOT_PASSWORD: password
      MYSQL_DATABASE: CAMEL
      MYSQL_USER: camel
      MYSQL_PASSWORD: abcdef
   ```
   
   camel.conf
   ```
   [database]
   HOST = camel-database
   NAME = CAMEL
   USER = camel
   PASSWORD = abcdef
   ``` 
   

5. Once ready, do the test run (following will: create Docker image, create isolated env (network), run Docker container; verify that web app works; clean up - stop and remove container, remove network):

   5.1. `docker-compose build` (or with env variables - see comments in Dockerfile under 'To get following env arguments filled')

   5.2. `docker-compose up -d`

   5.3. In browser, open: http://localhost:8888/. The webpage (of your Flask web app) should appear.
   
   5.4. `docker-compose down`

6. We assume that you have a database dump of MySQL in the root folder. 
   It could have been created via `mysqldump --add-drop-table -u admin -p`cat /etc/psa/.psa.shadow` dbname > dbname.sql`
   
   This database dump could be imported in the database server once started by using 
   `mysql -u admin -p`cat /etc/psa/.psa.shadow` -h camel-database dbname < dbname.sql`

## Notes

- Uses Ubuntu 18.04 as a base image.

- This solution does not set up virtual/isolated Python environment (i.e., such created by virtualenv) but uses global python/pip,
because there is one running Flask app. To change this (for example, in order to have many Flask apps on same container or there is other situation that require different isolated Python environments), additional work is needed to set up virtual Python environments (need to do changes to Dockerfile).

- Though not paramount, attempts to have as minimal image (size) as possible.

- Dev env specifics: docker-compose 1.22.0,  Docker 18.06.1-ce

- **Corresponding Docker images are automatically built to (and can be pulled from) public repository at:** https://hub.docker.com/r/dm4rnde/flask-app-base-apache2-wsgi-py3-ubuntu/
