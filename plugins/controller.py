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
        end = datetime(now.year,now.month,now.day,23,59,59)

        if(term == "yesterday"):
            st = now + timedelta(days=-1)
        elif(term == "week"):
            st = now + timedelta(days=-6)

        start = datetime(st.year,st.month,st.day,0,0,0)
        return {"start": start, "end": end}

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

    def list(self, uid, opt):
        term = opt.term

        if term == '':
            term = "today"

        now = datetime.now()
        d = self.term_to_time_duration(now, term)
        tasklist = self.db.get_task_list(uid, d["start"].strftime('%Y/%m/%d %H:%M:%S'), d["end"].strftime('%Y/%m/%d %H:%M:%S'))

        msg = "\n"
        workedtime = timedelta(0)
        ## when -sum is NOT specified
        if opt.sum == False:
            for row in tasklist:
                if(row['start'] is not None and row['end'] is not None):
                    diftime = self.get_task_time(d["start"], d["end"], row['start'], row['end'])
                    msg += row['name'] + ": " + str(diftime) + "\t(" + row['start'].strftime('%m/%d %H:%M') + " ~ " + row['end'].strftime('%m/%d %H:%M') + ")\n"
                    workedtime += diftime
            msg += term + "'s working time: " + str(workedtime)
            return msg

        ## when -sum is specified
        dict = {}
        for row in tasklist:
            if(row['start'] is not None and row['end'] is not None):
                diftime = self.get_task_time(d["start"], d["end"], row['start'], row['end'])
                if(not row['name'] in dict):
                    dict[row['name']] = diftime
                else:
                    dict[row['name']] += diftime
        for k,v in dict.items():
            msg += k + ": " + str(v) + "\n"
            workedtime += v
        msg += term + "'s working time: " + str(workedtime)
        return msg

    def start_task(self, ts, uid, opt):
        now = datetime.now()
        ## nameの指定は必須
        if opt.tname == '':
            return "task name is required."
        task_name = opt.tname

        ## -bの指定があるか
        if opt.begin == '':
            time = datetime.fromtimestamp(float(ts)).strftime('%Y/%m/%d %H:%M:%S')
        else:
            strtime = opt.begin.split(":")
            time = datetime(now.year, now.month, now.day, int(strtime[0]), int(strtime[1]), 0).strftime('%Y/%m/%d %H:%M:%S')

        self.db.register_task(uid, task_name, time)

        return "Add " + task_name

    def finish_task(self, ts, uid, opt):
        now = datetime.now()
        result = -1

        ## if tname is not specified, use current task
        task_name = opt.tname
        if task_name == '':
            l = now + timedelta(hours=-12)
            limit = datetime(l.year, l.month, l.day, 0, 0, 0).strftime('%Y/%m/%d %H:%M:%S')
            task = self.db.get_current_task(uid, limit)
            task_name = task['name']

        if opt.finish == '':
            time = datetime.fromtimestamp(float(ts)).strftime('%Y/%m/%d %H:%M:%S')
        else:
            strtime = opt.finish.split(":")
            time = datetime(now.year, now.month, now.day, int(strtime[0]), int(strtime[1]), 0).strftime('%Y/%m/%d %H:%M:%S')

        result = self.db.finish_task(uid, task_name, time)

        if(result == 0):
            return task_name + "を終了"
        else:
            return "終了処理が追加できませんでした（userがない，タスク名がない，時刻がおかしい,etc...）"

    def show_current_task(self, uid):
        now = datetime.now()
        l = now + timedelta(hours=-12)
        limit = datetime(l.year, l.month, l.day, 0, 0, 0).strftime('%Y/%m/%d %H:%M:%S')
        task = self.db.get_current_task(uid, limit)
        if(task == None):
            return "There is no task..."

        start_time = task['start'].strftime('%Y/%m/%d %H:%M:%S')
        return "The latest task is '''" + task['name'] + "''',    " + "started at " + start_time

