# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from plugins.storage import MySQL

class Controller:
    def __init__(self, test):
        self.db = MySQL(test)

    def register_user(self, uid, user_name):
        self.db.register_user(uid, user_name)
        self.db.show_users()

    def term_to_time_duration(self, now, term):
        # default is "today"
        st = now
        finish = datetime(now.year,now.month,now.day,23,59,59)

        if(term == "yesterday"):
            st = now + timedelta(days=-1)
        elif(term == "week"):
            st = now + timedelta(days=-6)

        start = datetime(st.year,st.month,st.day,0,0,0)
        return (start, finish)

    def get_task_time(self, s, e, rs, re):
        start = rs
        end = re
        # 日付超え対応, start_timeより前だったり、endより後のものはいれない
        if(rs < s):
            ## 次の日の0時
            rs += timedelta(days=+1)
            start = datetime(rs.year, rs.month, rs.day,0,0,0)
        if(re > e):
            ## 前の日の0時1秒前
            re += timedelta(days=-1)
            end = datetime(re.year, re.month, re.day,23,59,59)

        return end - start

    def out(self, uid, term):
        now = datetime.now()
        d = self.term_to_time_duration(now, term)
        tasklist = self.db.get_task_list(uid, d[0].strftime('%Y/%m/%d %H:%M:%S'), d[1].strftime('%Y/%m/%d %H:%M:%S'))

        msg = "\n"
        workedtime = timedelta(0)
        for row in tasklist:
            if(row['start'] is not None and row['end'] is not None):
                diftime = self.get_task_time(d[0], d[1], row['start'], row['end'])
                msg += row['name'] + ": " + str(diftime) + "\t(" + row['start'].strftime('%m/%d %H:%M') + " ~ " + row['end'].strftime('%m/%d %H:%M') + ")\n"
                workedtime += diftime
        msg += term + "'s working time: " + str(workedtime)
        return msg

    # nameが同じものを集計する
    def summary(self, uid, term):
        now = datetime.now()
        d = self.term_to_time_duration(now, term)
        tasklist = self.db.get_task_list(uid, d[0], d[1])

        msg = "\n"
        workedtime = timedelta(0)
        dict = {}
        for row in tasklist:
            if(row['start'] is not None and row['end'] is not None):
                diftime = self.get_task_time(d[0], d[1], row['start'], row['end'])
                if(not row['name'] in dict):
                    dict[row['name']] = diftime
                else:
                    dict[row['name']] += diftime
        for k,v in dict.items():
            msg += k + ": " + str(v) + "\n"
            workedtime += v
        msg += term + "'s working time: " + str(workedtime)
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

