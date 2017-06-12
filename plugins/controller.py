# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from plugins.storage import MySQL
import re

class Controller:
    def __init__(self, test):
        self.db = MySQL(test)
        self.re_ydt  = re.compile("[0-9]{4}\/[0-9]{1,2}\/[0-9]{1,2}-[0-9]{1,2}:[0-9]{1,2}")
        self.re_dt   = re.compile("[0-9]{1,2}\/[0-9]{1,2}-[0-9]{1,2}:[0-9]{1,2}")
        self.re_time = re.compile("[0-9]{1,2}:[0-9]{1,2}")

    def register_user(self, uid, user_name):
        self.db.register_user(uid, user_name)
        self.db.show_users()

    def term_to_time_duration(self, now, term):
        # default is "today"
        st = now
        finish = datetime(now.year,now.month,now.day,23,59,59)

        if(term == "yesterday"):
            st = now + timedelta(days=-1)
            finish = datetime(st.year,st.month,st.day,23,59,59)
        elif(term == "week"):
            st = now + timedelta(days=-6)

        begin = datetime(st.year,st.month,st.day,0,0,0)
        return {"begin": begin, "finish": finish}

    def get_task_time(self, s, e, rs, re):
        begin = rs
        finish = re
        # 日付超え対応, begin_timeより前だったり、finishより後のものはいれない
        if(rs < s):
            ## 次の日の0時
            rs += timedelta(days=+1)
            begin = datetime(rs.year, rs.month, rs.day,0,0,0)
        if(re > e):
            ## 前の日の0時1秒前
            re += timedelta(days=-1)
            finish = datetime(re.year, re.month, re.day,23,59,59)

        return finish - begin

    def str_to_datetime(self, str):
        now = datetime.now()
        dt = None
        if self.re_ydt.search(str) != None:
            dt = datetime.strptime(str, '%Y/%m/%d-%H:%M')
        elif self.re_dt.search(str) != None:
            dt = datetime.strptime(now.strftime('%Y/')+str, '%Y/%m/%d-%H:%M')
        elif self.re_time.search(str) != None:
            dt = datetime.strptime(now.strftime('%Y/%m/%d')+"-"+str, '%Y/%m/%d-%H:%M')

        return dt

    def timedelta_to_hhmmss(self, timedel):
    	hour = timedel.seconds // 3600 + timedel.days * 24
    	minutes = timedel.seconds % 3600 // 60
    	seconds = timedel.seconds % 3600 % 60
    	strmin = str(int(minutes)) if int(minutes) >= 10 else "0" + str(int(minutes))
    	strsec = str(int(seconds)) if int(seconds) >= 10 else "0" + str(int(seconds))
    	displayTime = str(int(hour)) + ":" + strmin +  ":" + strsec
    	return displayTime

    def list(self, uid, opt):
        term = opt.term

        if opt.begin == '' and opt.finish == '':
            if term == '':
                term = "today"
            now = datetime.now()
            d = self.term_to_time_duration(now, term)
            dt_begin  = d["begin"]
            dt_finish = d["finish"]
        else:
            dt_begin  = self.str_to_datetime(opt.begin)
            dt_finish = self.str_to_datetime(opt.finish)

        tasklist = self.db.get_task_list(uid, dt_begin.strftime('%Y/%m/%d %H:%M:%S'), dt_finish.strftime('%Y/%m/%d %H:%M:%S'))

        msg = "\n"
        workedtime = timedelta(0)
        ## when -sum is NOT specified
        if opt.sum == False:
            for row in tasklist:
                if(row['begin'] is not None and row['finish'] is not None):
                    diftime = self.get_task_time(dt_begin, dt_finish, row['begin'], row['finish'])
                    msg += row['name'] + ": " + str(diftime) + "\t(" + row['begin'].strftime('%m/%d %H:%M') + " ~ " + row['finish'].strftime('%m/%d %H:%M') + ")\n"
                    workedtime += diftime
            msg += term + "'s working time: " + self.timedelta_to_hhmmss(workedtime)
            return msg

        ## when -sum is specified
        dict = {}
        for row in tasklist:
            if(row['begin'] is not None and row['finish'] is not None):
                diftime = self.get_task_time(dt_begin, dt_finish, row['begin'], row['finish'])
                if(not row['name'] in dict):
                    dict[row['name']] = diftime
                else:
                    dict[row['name']] += diftime
        for k,v in sorted(dict.items()):
            msg += k + ": " + self.timedelta_to_hhmmss(v) + "\n"
            workedtime += v
        msg += term + "'s working time: " + self.timedelta_to_hhmmss(workedtime)
        return msg

    def begin_task(self, ts, uid, opt):
        ## nameの指定は必須
        if opt.tname == '':
            return "task name is required."
        task_name = opt.tname

        ## -bの指定があるか
        if opt.begin == '':
            dt = datetime.fromtimestamp(float(ts)).strftime('%Y/%m/%d %H:%M:%S')
        else:
            dt = self.str_to_datetime(opt.begin)

        if dt == None:
            return "Failed to convert specified time to datetime"

        self.db.register_task(uid, task_name, dt)

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
            dt = datetime.fromtimestamp(float(ts)).strftime('%Y/%m/%d %H:%M:%S')
        else:
            dt = self.str_to_datetime(opt.finish)

        if dt == None:
            return "Failed to convert specified time to datetime"

        result = self.db.finish_task(uid, task_name, dt)

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

        begin_time = task['begin'].strftime('%Y/%m/%d %H:%M:%S')
        return "The latest task is '''" + task['name'] + "''',    " + "begined at " + begin_time

