# -*- coding: utf-8 -*-
import argparse
from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ
from plugins.controller import Controller
import shlex

parser = argparse.ArgumentParser(prog='task')
parser.add_argument('command', help='sub command value', default='')
parser.add_argument('tname', help='task name', nargs='?', default='')
parser.add_argument('-begin', help='begin time', default='')
parser.add_argument('-finish', help='finish time', default='')
parser.add_argument('-edit', help='edit number', default='')
parser.add_argument('-term', help='term (today(default), yesterday, week)', default='')
parser.add_argument('-sum', help='summalize flag', action='store_true')
parser.add_argument('-every', help='repeat interval', default='')
parser.add_argument('-instraction', help='instraction(sub command with options)', default='')

test_flag = 0
ct = Controller(test_flag, parser)


@respond_to(r"^addReport")
def add_report(msg):
    uid = msg.body['user']
    text = msg.body['text']
    options = parser.parse_args(shlex.split(text))
    result_msg = ct.register_report(uid, text, options, msg.body['channel'])
    msg.reply(result_msg)

@listen_to(r"^showReports")
def show_reports(msg):
    uid = msg.body['user']
    ret = ct.show_reports(uid)
    msg.reply(ret)

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
        ["now                      ", "直近の終了していないタスクの表示"],
        ["@bot addReport [-b time] [-every day|Monday-Sunday] [-i command] ", "commandで取得できるタスク一覧を指定した時刻に投稿するレポート要求を追加"],
        ["showReports      ", "自分が登録しているレポート要求一覧の表示"],
    ]
    ret = "\n"
    for c in commands:
        ret += c[0] + "-- " + c[1] + "\n"
    msg.reply(ret)

