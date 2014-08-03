# !~/.virtualenvs/py3.3/bin/python
# -*- coding:utf-8 -*-

import re
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import json
from twitter import *

def get_value(path):
    '''
    sumGaphに格納された日付と経路数をListに格納して戻す
    '''

    graphvalue = []
    graphdate = []
    
    valueregex = re.compile(',(.+$)')
    dateregex = re.compile('(^.+),')

    for line in open(path, 'r'):
        graphvalue.append("".join(valueregex.findall(line)))

        src = "".join(dateregex.findall(line))
        src = src.replace('/', ',', 2)
        srclist = src.split(',')
        src = datetime.date(int(srclist[0]), int(srclist[1]), int(srclist[2]))
        graphdate.append(src)
    
    return graphvalue, graphdate

# ----------------------------------------------

def make_graph(value,date):
    '''
    日付と値のリストを利用してグラフを描画する
    '''

    x = []
    y = []

    x = date
    y = value

    startday = str(date[0])
    stopday = str(date[len(date)-1])

    fig = plt.figure()
    axes = fig.add_subplot(111)
    #グラフの定義
    axes.grid()
    axes.set_xlabel('date')
    axes.set_ylabel('routes')
    axes.set_title('IPv6 advertized route('+startday+' - '+stopday+')')
    
    #グラフを描画
    axes.plot(x, y)
    days = mdates.AutoDateLocator()
    daysFmt = mdates.DateFormatter('%Y-%m')
    axes.xaxis.set_major_locator(days)
    axes.xaxis.set_major_formatter(daysFmt)
    fig.autofmt_xdate()

    fig.savefig('/var/www/html/images/IPv6-fullroute.png')
    plt.clf()

# ----------------------------------------------

def post_twitter(txt):
    '''
    twitterにPostする
    '''

    # jsonから認証情報を取得する
    f = open('/opt/ipv6kuma_v2/twitter.json')
    date = json.load(f)
    f.close

    key = date[0]["consumer_key"]
    secret = date[0]["consumer_secret"]
    token = date[0]["oauth_token"]
    token_secret = date[0]["oauth_token_secret"]

    # 受け取った文字列をPostする
    t = Twitter(auth=OAuth(token, token_secret, key, secret))
    t.statuses.update(status=txt)

# ----------------------------------------------

def main():
    '''
    メイン処理
    '''

    txt_path = "/opt/ipv6kuma_v2/fullroute-check/sumGraph.txt"
    #ファイルからグラフの描画に必要なデータを取得する
    value, date = get_value(txt_path)

    #取得したデータを元にグラフを描画する
    make_graph(value, date)

    #グラフができたことをPostする
    updatetext = "本日までの経路数をグラフにしたクマ!!http://aimless.jp/images/IPv6-fullroute.png"
    post_twitter(updatetext)

if __name__ == '__main__':
    main()
