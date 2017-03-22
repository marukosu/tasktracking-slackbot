from slackbot.bot import respond_to     # @botname: で反応するデコーダ
from slackbot.bot import listen_to      # チャネル内発言で反応するデコーダ
from slackbot.bot import default_reply  # 該当する応答がない場合に反応するデコーダ
from datetime import datetime, timedelta
import mysql

#startの挿入
#bool isok start_task(string user_id, string task_name, timestamp stat_time)
#finishの挿入
#int error_code finish_task(string user_id, string task_name, timestamp finish_time)
#指定範囲の時刻のタスクリスト取得
#task[] records get_tasks_by_time_range(string user_id, timestamp start_time, timestamp finish_time)
#ユーザーの登録
#int ret register(user_id, user_name)

db = mysql.MySQL()

#@default_reply()
#def default_func(message):
#    text = message.body['text']     # メッセージを取り出す
    # 送信メッセージを作る。改行やトリプルバッククォートで囲む表現も可能
#    msg = 'yourself'
#    message.send(msg)      # メンション

#ユーザー登録処理
@respond_to(r"^register me")
def register_user(message):
    user_id = message.body['user']
    user_name = message.channel._client.users[message.body['user']]['name']
    db.registerUser(user_id, user_name)
    db.showUsers()

#タスク集計処理(現状"today","yesterday"のみ)
@respond_to(r"^out_")
def get_results(message):
    text = message.body['text']
    splitted = text.split('_')
    now = datetime.now()

    user_id = message.body['user']
    term = splitted[1]

    if(term == "today"):
        y = now.year
        m = now.month
        d = now.day
        start_time = datetime(y,m,d,0,0,0).strftime('%Y/%m/%d %H:%M:%S')
        finish_time = datetime(y,m,d,23,59,59).strftime('%Y/%m/%d %H:%M:%S')
        tasklist = db.getTaskList(user_id, start_time, finish_time)

    if(term == "yesterday"):
        now = now + timedelta(days=-1)
        y = now.year
        m = now.month
        d = now.day
        start_time = datetime(y,m,d,0,0,0).strftime('%Y/%m/%d %H:%M:%S')
        finish_time = datetime(y,m,d,23,59,59).strftime('%Y/%m/%d %H:%M:%S')
        tasklist = db.getTaskList(user_id, start_time, finish_time)
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
    text = message.body['text']
    splitted = text.split('_')
    num = len(splitted)

    user_id = message.body['user']
    task_name = splitted[1]

    if(num == 2 and len(splitted[1]) != 0): #時間指定なしなら投稿の時刻を利用
        time = datetime.fromtimestamp(float(message.body["ts"])).strftime('%Y/%m/%d %H:%M:%S')
        db.registerTask(user_id, task_name, time)

    if(num == 3 and len(splitted[2]) != 0): #時間指定ありならlinuxtimestanpに変換して利用
        strtime = splitted[2].split(":")
        now = datetime.now()

        y = now.year
        m = now.month
        d = now.day
        hh = int(strtime[0])
        mm = int(strtime[1])
        ss = 0
        time = datetime(y,m,d,hh,mm,ss).strftime('%Y/%m/%d %H:%M:%S')
        db.registerTask(user_id, task_name, time)

#"f_"コマンドの処理
@listen_to(r"^f_|^e_")
def listen_f(message):
    text = message.body['text']
    splitted = text.split('_')
    num = len(splitted)

    user_id = message.body['user']
    task_name = splitted[1]

    if(num == 2 and len(splitted[1]) != 0): #時間指定なしなら投稿の時刻を利用
        time = datetime.fromtimestamp(float(message.body["ts"])).strftime('%Y/%m/%d %H:%M:%S')
        result = db.finishTask(user_id, task_name, time)

    if(num == 3 and len(splitted[2]) != 0): #時間指定ありならlinuxtimestanpに変換して利用
        strtime = splitted[2].split(":")
        now = datetime.now()

        y = now.year
        m = now.month
        d = now.day
        hh = int(strtime[0])
        mm = int(strtime[1])
        ss = 0
        time = datetime(y,m,d,hh,mm,ss).strftime('%Y/%m/%d %H:%M:%S')
        result = db.finishTask(user_id, task_name, time)
    if(result == -1):
        message.reply("終了処理が追加できませんでした（userがない，タスク名がない，時刻がおかしい,etc...）")

