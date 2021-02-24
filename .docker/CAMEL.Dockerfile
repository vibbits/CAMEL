FROM ubuntu:18.04

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y apache2 libmysqlclient-dev build-essential libapache2-mod-wsgi-py3 --no-install-recommends
# RUN a2enmod wsgi
RUN a2enmod rewrite
RUN a2enmod proxy_http

RUN mkdir /var/www/CAMEL

RUN adduser --system --group --disabled-login camel ; cd /home/camel/
RUN chown -R camel:www-data /var/www/CAMEL

COPY CAMELApache.conf /etc/apache2/sites-available/CAMEL.conf
RUN a2ensite CAMEL

RUN rm -rf /etc/apache2/sites-available/000-default.conf
RUN rm -rf /etc/apache2/sites-enabled/000-default.conf

RUN chown -R camel:www-data /var/www/CAMEL

EXPOSE 80 443


ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.version=$VERSION \
      org.label-schema.license="MIT" \
      org.label-schema.name="Docker image with flask app base (using apache2, wsgi, py3, ubuntu)" \
      org.label-schema.description="Docker image to create docker container from, that accommodates Flask web app which relies on Apache 2, wsgi, Python 3, and Ubuntu." \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/dm4rnde/docker-flask-app-base-apache2-wsgi-py3" \
      org.label-schema.docker.schema-version="1.0"

ENTRYPOINT ["/bin/bash", "/usr/sbin/apache2ctl", "-D", "FOREGROUND"]
