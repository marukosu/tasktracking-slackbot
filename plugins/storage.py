# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.sql import text


class MySQL:
    def __init__(self, test):
        if test == 1:
            self.engine = create_engine(
                "mysql+pymysql://slack:slack@127.0.0.1:13306/slack?charset=utf8",
                encoding='utf-8',
                echo=True,
                pool_size=10,
                pool_recycle=1000,
            )
            return
        self.engine = create_engine(
            "mysql://root:root@localhost/slack?charset=utf8",
            encoding='utf-8',
            echo=False,
            pool_size=10,
            pool_recycle=1000,
        )

    def show_users(self):
        conn = self.engine.connect()
        s = text("SELECT id, name FROM users")
        rows = conn.execute(s).fetchall()

    def register_user(self, id, name):
        conn = self.engine.connect()
        s = text("INSERT INTO users (id, name) VALUES (:i, :n) ON DUPLICATE KEY UPDATE name = :n")
        conn.execute(s, i=id, n=name)

    def register_task(self, uid, taskName, beginTime):
        conn = self.engine.connect()
        s = text("INSERT INTO tasks (uid, name, begin) VALUES (:u, :n, :s)")
        conn.execute(s, u=uid, n=taskName, s=beginTime)

    def finish_task(self, uid, taskName, finishTime):
        conn = self.engine.connect()
        s = text("SELECT id, begin FROM tasks WHERE uid = :u AND name = :n AND finish is NULL ORDER BY id DESC LIMIT 1")
        task = conn.execute(s, u=uid, n=taskName).fetchone()
        if task is None:
            return -1
        id = task['id']
        begin_time = task['begin']
        s = text("UPDATE tasks SET finish = :e WHERE id = :i")
        conn.execute(s, e=finishTime, i=id)

        return 0, begin_time

    def get_task_list(self, uid, fromTime, toTime):
        conn = self.engine.connect()
        s = text("SELECT name, begin, finish FROM tasks WHERE uid = :u AND finish > :f AND (begin < :t OR finish IS NULL)")
        tasklist = conn.execute(s, u=uid, f=fromTime, t=toTime).fetchall()

        return tasklist

    def get_current_task(self, uid, limit):
        conn = self.engine.connect()
        s = text("SELECT name, begin FROM tasks WHERE uid = :u AND finish IS NULL AND begin > :l ORDER BY begin DESC LIMIT 1")
        task = conn.execute(s, u=uid, l=limit).fetchone()
        return task

    def get_latest_task_list(self, uid, task_number):
        conn = self.engine.connect()
        s = text("SELECT name, id, begin, finish FROM tasks WHERE uid = :u ORDER BY begin DESC LIMIT " + str(task_number))
        task_list = conn.execute(s, u=uid).fetchall()
        return task_list

    def register_report(self, uid, every, at, command, channel):
        conn = self.engine.connect()
        s = text("INSERT INTO reports (uid, every, at, command, channel) VALUES (:u, :e, :a, :c, :ch)")
        ret = conn.execute(s, u=uid, e=every, a=at, c=command, ch=channel)
        return ret.lastrowid

    def get_report_list(self, uid = None):
        conn = self.engine.connect()
        if uid == None:
            s = text("SELECT r.id, r.uid, u.name, r.every, r.at, r.command, r.channel, r.created_at, r.updated_at FROM reports r INNER JOIN users u ON r.uid = u.id ORDER BY u.name ASC")
            reports = conn.execute(s).fetchall()
        else:
            s = text("SELECT r.id, r.uid, u.name, r.every, r.at, r.command, r.channel, r.created_at, r.updated_at FROM reports r INNER JOIN users u ON r.uid = u.id WHERE u.id = :u ORDER BY r.id ASC")
            reports = conn.execute(s, u=uid).fetchall()

        return reports
