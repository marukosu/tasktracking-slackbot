# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from plugins.storage import MySQL

class Controller:
    def __init__(self, test):
        self.db = MySQL(test)

    def register_user(self, uid, user_name):
        self.db.register_user(uid, user_name)
        self.db.show_users()

    def summary(self, uid, term):
        now = datetime.now()
        if(term == "today"):
            start_time = datetime(now.year,now.month,now.day,0,0,0).strftime('%Y/%m/%d %H:%M:%S')
            finish_time = datetime(now.year,now.month,now.day,23,59,59).strftime('%Y/%m/%d %H:%M:%S')
            tasklist = self.db.get_task_list(uid, start_time, finish_time)
        elif(term == "yesterday"):
            yd = now + timedelta(days=-1)
            start_time = datetime(yd.year,yd.month,yd.day,0,0,0).strftime('%Y/%m/%d %H:%M:%S')
            finish_time = datetime(yd.year,yd.month,yd.day,23,59,59).strftime('%Y/%m/%d %H:%M:%S')
            tasklist = self.db.get_task_list(uid, start_time, finish_time)
        else:
            return "Not supported " + term

        msg = "\n"
        workedtime = timedelta(0)
        for row in tasklist:
            if(row['start'] is not None and row['end'] is not None):
                diftime = row['end'] - row['start']
                msg += row['name'] + ": " + str(diftime) + "\n"
                workedtime += diftime
        msg += "today's working time: " + str(workedtime)
        return msg

    def start_task(self, ts, uid, text):
        now = datetime.now()
        splitted = text.split('_')
        num = len(splitted)
        task_name = splitted[1]

        if(num == 2 and len(splitted[1]) != 0): #時間指定なしなら投稿の時刻を利用
            time = datetime.fromtimestamp(float(ts)).strftime('%Y/%m/%d %H:%M:%S')
            self.db.register_task(uid, task_name, time)
        if(num == 3 and len(splitted[2]) != 0): #時間指定ありならlinuxtimestanpに変換して利用
            strtime = splitted[2].split(":")
            time = datetime(now.year, now.month, now.day, int(strtime[0]), int(strtime[1]), 0).strftime('%Y/%m/%d %H:%M:%S')
            self.db.register_task(uid, task_name, time)

        return "Add " + task_name

    def finish_task(self, ts, uid, text):
        now = datetime.now()
        result = -1
        splitted = text.split('_')
        task_name = splitted[1]
        num = len(splitted)

        if(num < 2):
            result = -1
        elif(num == 2): #時間指定なしなら投稿の時刻を利用
            time = datetime.fromtimestamp(float(ts)).strftime('%Y/%m/%d %H:%M:%S')
            result = self.db.finish_task(uid, task_name, time)
        elif(num == 3): #時間指定ありならlinuxtimestanpに変換して利用
            strtime = splitted[2].split(":")
            time = datetime(now.year, now.month, now.day, int(strtime[0]), int(strtime[1]), 0).strftime('%Y/%m/%d %H:%M:%S')
            result = self.db.finish_task(uid, task_name, time)

        if(result == 0):
            return task_name + "を終了"
        else:
            return "終了処理が追加できませんでした（userがない，タスク名がない，時刻がおかしい,etc...）"

    def finish_current_task(self, ts, uid):
        result = -1

        now = datetime.now()
        l = now + timedelta(hours=-12)
        limit = datetime(l.year, l.month, l.day, 0, 0, 0).strftime('%Y/%m/%d %H:%M:%S')
        task = self.db.get_current_task(uid, limit)

        time = datetime.fromtimestamp(float(ts)).strftime('%Y/%m/%d %H:%M:%S')
        result = self.db.finish_task(uid, task['name'], time)

        if(result == 0):
            return task['name'] + "を終了"
        else:
            return "終了処理が追加できませんでした"

    def show_current_task(self, uid):
        now = datetime.now()
        l = now + timedelta(hours=-12)
        limit = datetime(l.year, l.month, l.day, 0, 0, 0).strftime('%Y/%m/%d %H:%M:%S')
        task = self.db.get_current_task(uid, limit)
        if(task == None):
            return "There is no task..."

        start_time = task['start'].strftime('%Y/%m/%d %H:%M:%S')
        return "The latest task is '''" + task['name'] + "''',    " + "started at " + start_time

