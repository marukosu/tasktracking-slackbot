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
@respond_to(r"^results_")
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
        start_time = datetime(y,m,d,0,0,0).strftime('%s')
        finish_time = datetime(y,m,d,23,59,59).strftime('%s')
        #get_tasks_by_time_range

    if(term == "yesterday"):
        if(now.day == 1):
            now = now + timedelta(days=-1)
        y = now.year
        m = now.month
        d = now.day
        start_time = datetime(y,m,d,0,0,0).strftime('%s')
        finish_time = datetime(y,m,d,23,59,59).strftime('%s')
        #get_tasks_by_time_range

#"s_"コマンドの処理
@listen_to(r"^s_")
def listen_s(message):
    text = message.body['text']
    splitted = text.split('_')
    num = len(splitted)

    user_id = message.body['user']
    task_name = splitted[1]

    if(num == 2 and len(splitted[1]) != 0): #時間指定なしなら投稿の時刻を利用
        time = message.body["ts"]
        #start_task

    if(num == 3 and len(splitted[2]) != 0): #時間指定ありならlinuxtimestanpに変換して利用
        strtime = splitted[2].split(":")
        now = datetime.now()

        y = now.year
        m = now.month
        d = now.day
        hh = int(strtime[0])
        mm = int(strtime[1])
        ss = now.second
        time = datetime(y,m,d,hh,mm,ss).strftime('%s')
        #start_task

#"f_"コマンドの処理
@listen_to(r"^f_")
def listen_f(message):
    text = message.body['text']
    splitted = text.split('_')
    num = len(splitted)

    user_id = message.body['user']
    task_name = splitted[1]

    if(num == 2 and len(splitted[1]) != 0): #時間指定なしなら投稿の時刻を利用
        time = message.body["ts"]
        #finish_task

    if(num == 3 and len(splitted[2]) != 0): #時間指定ありならlinuxtimestanpに変換して利用
        strtime = splitted[2].split(":")
        now = datetime.now()

        y = now.year
        m = now.month
        d = now.day
        hh = int(strtime[0])
        mm = int(strtime[1])
        ss = now.second
        time = datetime(y,m,d,hh,mm,ss).strftime('%s')
        #finish_task

