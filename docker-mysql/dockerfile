FROM mysql:5.7
MAINTAINER tom__bo

COPY conf/setting.cnf /etc/mysql/conf.d/
COPY initdb/setting.sql /docker-entrypoint-initdb.d/

ENV MYSQL_ROOT_PASSWORD=root \
    MYSQL_USER=slack \
    MYSQL_PASSWORD=slack \
    MYSQL_DATABASE=slack \
    MYSQL_PORT=3306 \

EXPOSE=13306


