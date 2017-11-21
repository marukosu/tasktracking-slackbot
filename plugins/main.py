# -*- coding: utf-8 -*-
import argparse
from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ
from datetime import datetime, timedelta
from plugins.controller import Controller
from plugins.reporter import Reporter
import time

test_flag = 0
ct = Controller(test_flag)
rp = Reporter(ct)

parser = argparse.ArgumentParser(prog='task')
parser.add_argument('command', help='sub command value', default='')
parser.add_argument('tname', help='task name', nargs='?', default='')
parser.add_argument('-begin', help='begin time', default='')
parser.add_argument('-finish', help='finish time', default='')
parser.add_argument('-edit', help='edit number', default='')
parser.add_argument('-term', help='term (today(default), yesterday, week)', default='')
parser.add_argument('-sum', help='summalize flag', action='store_true')
parser.add_argument('-repeat', help='repeat time', default='')

#日毎と週ごとのタスクトラッキングデータを出力（今後dayとweekで分けても良い）
@respond_to(r"^startReport|^stopReport|^stopAllReport")
def cron_report(msg):
    uid = msg.body['user']
    text = msg.body['text']
    #将来,contorollerのlist_for_reportではなくlistを使用し
    #optionsによってユーザーごとにタスクの集計範囲を分ける可能性があります
    #options = parser.parse_args(text.split())
    if text == "startReport":
        rep = rp.add_user(uid,msg)
        msg.reply(rep)
    elif text == "stopReport":
        rep = rp.remove_user(uid)
        msg.reply(rep)
    elif text == "stopAllReport":
        rp.stop_report(msg)

#ユーザー登録処理
@respond_to(r"^register me")
def register(msg):
    uid = msg.body['user']
    uname = msg.channel._client.users[msg.body['user']]['name']
    ct.register_user(uid, uname)

#タスク一覧
@listen_to(r"^l$|^l |^list$|^list ")
def sum(msg):
    uid = msg.body['user']
    text = msg.body['text']
    options = parser.parse_args(text.split())
    ret = ct.list(uid, options)
    msg.reply(ret)

#"s_"コマンドの処理
@listen_to(r"^b |^begin ")
def begin(msg):
    ts = msg.body['ts']
    uid = msg.body['user']
    text = msg.body['text']
    options = parser.parse_args(text.split())
    ret = ct.begin_task(ts, uid, options)
    msg.reply(ret)

#"f_"コマンドの処理
@listen_to(r"^f$|^f |^finish$|^finish ")
def listen_f(msg):
    ts = msg.body['ts']
    uid = msg.body['user']
    text = msg.body['text']
    options = parser.parse_args(text.split())
    ret = ct.finish_task(ts, uid, options)
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
        ["begin(b) taskname [-b time]        ", "tasknameでタスクを開始。_12:00のように時間を指定することで時刻を遡って登録可能"],
        ["finish(f) taskname [-f time]        ", "tasknameのタスクを終了。_12:00のように時間を指定することで時刻を遡って登録可能"],
        ["list(l) [-sum] [-t today|yesterday|week] ", "指定した日の登録したタスク一覧を表示"],
        ["now                      ", "直近の終了していなタスクの表示"],
        ["@bot startReport         ", "毎日23:55にその日の登録されたタスクデータを投稿する．日曜日は週報も投稿する"]
        ["@bot stopReport          ", "タスクデータの定期投稿を停止する"]
        ["@bot stopAllReport          ", "全ユーザーのタスクデータの定期投稿を停止する（停止すべきユーザーが操作できない場合）"]
    ]
    ret = "\n"
    for c in commands:
        ret += c[0] + "-- " + c[1] + "\n"
    msg.reply(ret)

