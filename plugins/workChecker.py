# -*- coding: utf-8 -*-
from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ
from datetime import datetime, timedelta
import mysql

db = mysql.MySQL()

#ユーザー登録処理
@respond_to(r"^register me")
def register_user(message):
    user_id = message.body['user']
    user_name = message.channel._client.users[message.body['user']]['name']
    db.registerUser(user_id, user_name)
    db.showUsers()

#タスク集計処理(現状"today","yesterday"のみ)
@listen_to(r"^out")
def get_results(message):
    text = message.body['text']
    splitted = text.split('_')
    now = datetime.now()

    user_id = message.body['user']
    if len(splitted) < 2:
        term = "today"
    else:
        term = splitted[1]

    if(term == "today"):
        start_time = datetime(now.year,now.month,now.day,0,0,0).strftime('%Y/%m/%d %H:%M:%S')
        finish_time = datetime(now.year,now.month,now.day,23,59,59).strftime('%Y/%m/%d %H:%M:%S')
        tasklist = db.getTaskList(user_id, start_time, finish_time)
    elif(term == "yesterday"):
        now = now + timedelta(days=-1)
        start_time = datetime(now.year,now.month,now.day,0,0,0).strftime('%Y/%m/%d %H:%M:%S')
        finish_time = datetime(now.year,now.month,now.day,23,59,59).strftime('%Y/%m/%d %H:%M:%S')
        tasklist = db.getTaskList(user_id, start_time, finish_time)
    else:
        message.reply("Not supported " + term)

    msg = "\n"
    workedtime = timedelta(0)
    for row in tasklist:
        if(row[1] is not None and row[2] is not None):
            diftime = row[2] - row[1]
            msg += row[0] + ": " + str(diftime) + "\n"
            workedtime += diftime
    msg += "today's working time: " + str(workedtime)
    message.reply(msg)

#"s_"コマンドの処理
@listen_to(r"^s_")
def listen_s(message):
    now = datetime.now()
    user_id = message.body['user']
    text = message.body['text']
    splitted = text.split('_')
    num = len(splitted)
    task_name = splitted[1]

    if(num == 2 and len(splitted[1]) != 0): #時間指定なしなら投稿の時刻を利用
        time = datetime.fromtimestamp(float(message.body["ts"])).strftime('%Y/%m/%d %H:%M:%S')
        db.registerTask(user_id, task_name, time)
    if(num == 3 and len(splitted[2]) != 0): #時間指定ありならlinuxtimestanpに変換して利用
        strtime = splitted[2].split(":")
        time = datetime(now.year, now.month, now.day, int(strtime[0]), int(strtime[1]), 0).strftime('%Y/%m/%d %H:%M:%S')
        db.registerTask(user_id, task_name, time)

    message.reply("Add " + task_name)

#"f_"コマンドの処理
@listen_to(r"^f_|^e_")
def listen_f(message):
    now = datetime.now()
    result = -1
    user_id = message.body['user']
    text = message.body['text']
    splitted = text.split('_')
    num = len(splitted)
    task_name = splitted[1]

    if(num == 2 and len(splitted[1]) != 0): #時間指定なしなら投稿の時刻を利用
        time = datetime.fromtimestamp(float(message.body["ts"])).strftime('%Y/%m/%d %H:%M:%S')
        result = db.finishTask(user_id, task_name, time)
    if(num == 3 and len(splitted[2]) != 0): #時間指定ありならlinuxtimestanpに変換して利用
        strtime = splitted[2].split(":")
        time = datetime(now.year, now.month, now.day, int(strtime[0]), int(strtime[1]), 0).strftime('%Y/%m/%d %H:%M:%S')
        result = db.finishTask(user_id, task_name, time)

    if(result == 0):
        message.reply(task_name + "を終了")
    else:
        message.reply("終了処理が追加できませんでした（userがない，タスク名がない，時刻がおかしい,etc...）")


# 最新の終了していないタスクの表示
@listen_to("^now")
def show_current_task(message):
    uid = message.body['user']
    task = db.get_current_task(uid)
    start_time = task[1].strftime('%Y/%m/%d %H:%M:%S')
    msg = "The latest task is '''" + task[0] + "''',    " + "started at " + start_time
    message.reply(msg)

# helpの表示
@listen_to("^help")
def show_help(message):
    commands = [
        ["@bot register me         ", "コメントしたチャンネルでbotを使うことを宣言する"],
        ["s_taskname[_time]        ", "tasknameでタスクを開始。_12:00のように時間を指定することで時刻を遡って登録可能"],
        ["f_taskname[_time]        ", "tasknameのタスクを終了。_12:00のように時間を指定することで時刻を遡って登録可能"],
        ["out[_today | _yesterday] ", "その日の登録したタスク一覧を表示"],
    ]
    msg = "\n"
    for c in commands:
        msg += c[0] + "-- " + c[1] + "\n"
    message.reply(msg)


