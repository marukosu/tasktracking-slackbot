# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from plugins.storage import MySQL
from slacker import Slacker
from crontab import CronTab
import re
import sched
import time
import shlex
import slackbot_settings
import threading


class Controller:
    def __init__(self, test, parser):
        self.sender = Slacker(slackbot_settings.API_TOKEN)
        self.db = MySQL(test)
        self.parser = parser
        self.re_ydt  = re.compile("[0-9]{4}\/[0-9]{1,2}\/[0-9]{1,2}-[0-9]{1,2}:[0-9]{1,2}")
        self.re_dt   = re.compile("[0-9]{1,2}\/[0-9]{1,2}-[0-9]{1,2}:[0-9]{1,2}")
        self.re_time = re.compile("[0-9]{1,2}:[0-9]{1,2}")
        self.dow = {"Sun":0, "Mon":1, "Tue":2, "Wed":3, "Thu":4, "Fri":5, "Sat":6, "day":7}
        self.sc = sched.scheduler(time.time,time.sleep)
        self.th = threading.Thread(target=self.reporter, daemon=True)
        self.th.start()

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

    def register_report(self, uid, text, opt, channel_id):
        every = opt.every
        at = opt.begin
        command = opt.instraction
        channel = channel_id
        result_msg = "I report a result of \"{0}\" at {1} every {2}".format(command, at, every)
        try:
            self.list(uid,self.parser.parse_args(shlex.split(command)))
        except:
            result_msg = "\"{0}\" is not correct format".format(command)
            return result_msg
        try:
            self.str_to_datetime(at)
            self.dow[every]
        except:
            result_msg = "\"{0}\" is not correct format".format(text)
            return result_msg
        r_id = str(self.db.register_report(uid, every, at, command, channel))
        start_time = self.get_start_time(every,at)
        if start_time < self.get_next_update_time():
            th = threading.Thread(target=self.set_tmp_scheduler, daemon = True, args =(start_time, r_id))
            th.start()

        return result_msg

    def reporter(self):
        update_time = self.get_next_update_time()
        for row in self.db.get_report_list():
            start_time = self.get_start_time(row['every'],row['at'])
            report_id = row['id']
            if start_time <= update_time:
                self.sc.enter(start_time, 1, self.send_report, argument=(str(report_id)))
        self.sc.enter(update_time, 1, self.reporter)
        self.sc.run()

    #与えられた条件までの秒数を返します
    def get_start_time(self, every, at):
        target_dow = self.dow[every]
        target_time = self.str_to_datetime(at)
        if target_dow == 7:
            cron_format = "{0} {1} * * *".format(target_time.minute, target_time.hour)
        else:
            cron_format = "{0} {1} * * {2}".format(target_time.minute, target_time.hour, target_dow)

        return CronTab(cron_format).next(default_utc=False)

    def send_report(self,r_id):
        for row in self.db.get_report_list():
            if str(row['id']) == r_id:
                task_report = self.list(row['uid'], self.parser.parse_args(row['command'].split()))
                self.sender.chat.post_message(row['channel'], "----{0}'s report. id:{1}----{2}".format(row['name'],r_id, task_report), as_user=True)

    def get_next_update_time(self):
        return CronTab("0 0 * * *").next(default_utc=False)

    def set_tmp_scheduler(self, start_time, r_id):
        tmp_sc = sched.scheduler(time.time,time.sleep)
        tmp_sc.enter(start_time, 1, self.send_report, argument=(str(r_id),))
        tmp_sc.run()

    def show_reports(self, uid):
        reports = self.db.get_report_list(uid)
        msg = "{0} reports\n".format(reports[0]['name'])
        for row in reports:
            msg += "id:{0}, every:{1}, at:{2}, command: <{3}>\n".format(row['id'],row['every'],row['at'],row['command'])

        return msg