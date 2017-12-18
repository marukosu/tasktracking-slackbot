## setting sql

# create database slack;

use slack;

CREATE TABLE users (
	id   varchar(12) PRIMARY KEY,
	name varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE tasks (
	id        int PRIMARY KEY AUTO_INCREMENT,
	uid       varchar(12),
	name      varchar(50),
	begin     DATETIME NULL,
	finish    DATETIME NULL,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(uid) REFERENCES users(id),
	INDEX begin_time(begin)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE reports (
	id        int PRIMARY KEY AUTO_INCREMENT,
	uid       varchar(12),
	every     varchar(9),
	at        varchar(6),
	command   varchar(40),
	channel   varchar(21),
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	FOREIGN KEY(uid) REFERENCES users(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

