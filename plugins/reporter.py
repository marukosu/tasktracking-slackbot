# -*- coding: utf-8 -*-
from plugins.controller import Controller
import threading
import time
from crontab import CronTab
import math
from datetime import datetime, timedelta

class Reporter:

    def __init__(self, ct):
        self.report_userlist = {}
        self.ct = ct
        self.isrunning = False
        self.addlock = False
        self.th = threading.Thread(target=self.time_counter,daemon = True)
        self.th.start()


    def add_user(self,uid,msg):
        if self.addlock == False:
            self.report_userlist[uid] = msg
            self.isrunning = True
        else:
            return "現在レポートの停止待機中です．翌日以降に再度startReportで追加処理を試みて下さい．翌日も失敗する場合は管理者に連絡してください"

        if self.th.is_alive() == False:
            self.th = threading.Thread(target=self.time_counter,daemon = True)
            self.th.start()

        return "レポートを受け取るユーザーに追加しました．毎日23:55にタスクの集計結果が通知されます"

    def remove_user(self,uid):
        try:
            del self.report_userlist[uid]
            if len(self.report_userlist) == 0:
                isrunning = False
        except KeyError:
            return "レポートを受け取るユーザーとして追加されていません．startReportでユーザー登録できます．"

        return "レポートを受け取るユーザーから削除しました"

    #run.py自体は止めずにreport用threadを個人の権限で正常終了させるためのコマンド．
    def stop_report(self,msg):
        self.isrunning = False
        stopper = msg.channel._client.users[msg.body['user']]['name']
        stopmsg = stopper + "により，次回呼び出しで全ユーザーのレポートを終了します"
        for uid in self.report_userlist:
            self.report_userlist[uid].reply(stopmsg)
        self.report_userlist.clear()
        self.addlock = True

    def time_counter(self):
        while self.isrunning:
            entry = CronTab('55 23 * * *')
            next_seconds = math.ceil(entry.next())
            time.sleep(next_seconds)
            #日報を送信
            for uid in self.report_userlist:
                ret = self.ct.list_for_report(uid, "today")
                self.report_userlist[uid].reply(ret)
                #日曜日には週報も送信
                if datetime.now().weekday() == 6:
                    ret = self.ct.list_for_report(uid, "week")
                    self.report_userlist[uid].reply(ret)
        self.addlock = False
        print("thread finish!")
        