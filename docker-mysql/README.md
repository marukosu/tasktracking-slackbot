## Description

This is the MySQL environment with Docker to test slack_bot.
The following environment can be constructed with this docker component...
- USER: root, PASSWD: root
- USER: slack, PASSWD: slack
- PORT: 13306(exposed port), 3306(in the docker)
- DB: slack
  - table: users
  - table: tasks
  - please refer ./conf/setting.sql about these

## HOW TO USE

1. Build an image from dockerfile
2. Run from the image

ex)
```
docker build -t mysql57:slack .
docker run -d -p 13306:3306 --name mysql57slack mysql57:slack
```

then, you can access MySQL server like this...
```
mysql -u slack -p -h 127.0.0.1 -P 13306 slack
```
