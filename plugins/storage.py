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
            echo=True,
            pool_size=10,
            pool_recycle=1000,
        )

    def show_users(self):
        conn = self.engine.connect()
        s = text("SELECT id, name FROM users")
        rows = conn.execute(s).fetchall()
        for row in rows:
            print("ID:" + str(row['id']) + "  NAME:" + row['name'])

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
        s = text("SELECT id FROM tasks WHERE uid = :u AND name = :n AND finish is NULL ORDER BY id DESC LIMIT 1")
        task = conn.execute(s, u=uid, n=taskName).fetchone()
        if task is None:
            return -1
        id = task['id']
        s = text("UPDATE tasks SET finish = :e WHERE id = :i")
        conn.execute(s, e=finishTime, i=id)

        return 0

    def get_task_list(self, uid, fromTime, toTime):
        conn = self.engine.connect()
        s = text("SELECT name, begin, finish FROM tasks WHERE uid = :u AND finish > :f AND (begin < :t OR finish IS NULL)")
        tasklist = conn.execute(s, u=uid, f=fromTime, t=toTime).fetchall()

        for row in tasklist:
            print("Name:" + row['name'] + "  begin:" + str(row['begin']) + "  finish:" + str(row['finish']))
        return tasklist

    def get_current_task(self, uid, limit):
        conn = self.engine.connect()
        s = text("SELECT name, begin FROM tasks WHERE uid = :u AND finish IS NULL AND begin > :l ORDER BY begin DESC LIMIT 1")
        task = conn.execute(s, u=uid, l=limit).fetchone()
        return task

    def register_report(self, uid, time, interval, command):
        raise NotImplementedError

    def get_report_list(self, uid = nil):
        raise NotImplementedError

    def delete_report(self, uid, reportId):
        raise NotImplementedError

