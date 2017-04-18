# -*- coding: utf-8 -*-
from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ
from datetime import datetime, timedelta
from plugins.controller import Controller

test_flag = 0
ct = Controller(test_flag)

#ユーザー登録処理
@respond_to(r"^register me")
def register(msg):
    uid = msg.body['user']
    uname = msg.channel._client.users[msg.body['user']]['name']
    ct.register_user(uid, uname)

#タスク一覧
@listen_to(r"^out")
def sum(msg):
    uid = msg.body['user']
    text = msg.body['text']
    splitted = text.split('_')

    if len(splitted) < 2:
        term = "today"
    else:
        term = splitted[1]

    ret = ct.out(uid, term)
    msg.reply(ret)

#タスク集計処理
@listen_to(r"^sum")
def sum(msg):
    uid = msg.body['user']
    text = msg.body['text']
    splitted = text.split('_')

    if len(splitted) < 2:
        term = "today"
    else:
        term = splitted[1]

    ret = ct.summary(uid, term)
    msg.reply(ret)

#"s_"コマンドの処理
@listen_to(r"^s_")
def start(msg):
    ts = msg.body['ts']
    uid = msg.body['user']
    text = msg.body['text']

    ret = ct.start_task(ts, uid, text)
    msg.reply(ret)

#"f_"コマンドの処理
@listen_to(r"^f_|^e_")
def listen_f(msg):
    ts = msg.body['ts']
    uid = msg.body['user']
    text = msg.body['text']

    ret = ct.finish_task(ts, uid, text)
    msg.reply(ret)


# 最新の終了していないタスクの表示
@listen_to(r"^now$")
def show_current_task(msg):
    uid = msg.body['user']
    ret = ct.show_current_task(uid)
    msg.reply(ret)

# helpの表示
@listen_to(r"^help$")
def show_help(msg):
    commands = [
        ["@bot register me         ", "コメントしたチャンネルでbotを使うことを宣言する"],
        ["s_taskname[_time]        ", "tasknameでタスクを開始。_12:00のように時間を指定することで時刻を遡って登録可能"],
        ["f_taskname[_time]        ", "tasknameのタスクを終了。_12:00のように時間を指定することで時刻を遡って登録可能"],
        ["sum[_today | _yesterday] ", "指定した日の登録したタスク一覧を表示"],
        ["out[_today | _yesterday] ", "指定した日の登録したタスク一覧を表示"],
        ["now                      ", "直近の終了していなタスクの表示"],
    ]
    ret = "\n"
    for c in commands:
        ret += c[0] + "-- " + c[1] + "\n"
    msg.reply(ret)

