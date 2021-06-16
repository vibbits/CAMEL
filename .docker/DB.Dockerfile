FROM mysql:latest

COPY .docker/CAMEL.sql /docker-entrypoint-initdb.d/CAMEL.sql