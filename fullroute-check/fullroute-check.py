#!~/.virtualenvs/py3.3/bin/python
# -*- coding:utf-8 -*-

import requests
import re
import difflib
import shutil
import datetime
from twitter import *
import json
import telnetlib
import pexpect
import time

def get_fullroute():
    '''
    HEのスナップショットを取得し、ベストパスをファイルに書き込む
    '''
    
    # HEのスナップショットを取得
    html = requests.get('http://ipv6.he.net/bgpview/bgp-table-snapshot.txt')

    # 取得したスナップショットをファイルに書き込む
    with open('/opt/ipv6kuma_v2/fullroute-check/bgp-table-snapshot.txt',mode='w',encoding='utf-8') as f:
        f.write(html.content.decode('utf-8'))

    # 書き込んだファイルを読み込み、正規表現でベストパスを抽出し、ファイルに書き込む
    regex = re.compile(r'^\*>i([\da-zA-Z]{0,4}:)*\/\d{1,3}')
    newRoute = open('/opt/ipv6kuma_v2/fullroute-check/new-route.txt',mode='w',encoding='utf-8')
    with open('/opt/ipv6kuma_v2/fullroute-check/bgp-table-snapshot.txt',mode='r',encoding='utf-8') as f:
        for line in f:
            if regex.match(line):
                newRoute.write(regex.match(line).group() + '\n')

# ----------------------------------------------

def get_fullroute_wide():
    '''
    wideのroute-serverからフルルートを取得し、ベストパスをファイルに書き込む
    '''

    # wideのroute-serverに接続しフルルートを取得する。
    prompt = 'route-views.wide.routeviews.org> '

    telnet = pexpect.spawn('telnet route-views.wide.routeviews.org', timeout=15)
    telnet.expect(prompt)
    telnet.sendline('ter len 0')
    telnet.expect(prompt)
    telnet.sendline('show bgp ipv6 neighbors 2001:200:0:fe00::9d4:0 routes')
    telnet.expect(prompt)
    telnet.sendline('ter len 24')
    fullroute = telnet.before
    telnet.close

    with open('/opt/ipv6kuma_v2/fullroute-check/bgp-table-snapshot.txt',mode='w',encoding='utf-8') as f:
        f.write('{0}'.format(fullroute.decode('utf-8')))

    # 書き込んだファイルを読み込み、正規表現でベストパスを抽出し、ファイルに書き込む
    regex = re.compile(r'^\*.\s([\da-zA-Z]{0,4}:)*\/\d{1,3}')
    newRoute = open('/opt/ipv6kuma_v2/fullroute-check/new-route.txt',mode='w',encoding='utf-8')
    with open('/opt/ipv6kuma_v2/fullroute-check/bgp-table-snapshot.txt',mode='r',encoding='utf-8') as f:
        for line in f:
            if regex.match(line):
                newRoute.write(regex.match(line).group() + '\n')

# ----------------------------------------------$

def check_route():
    '''
    経路をチェックし、ブイロクマのコメントを返す
    '''

    # 本日と先日の経路数を確認する
    with open('/opt/ipv6kuma_v2/fullroute-check/new-route.txt',mode='r',encoding='utf-8') as f:
        today_route = sum(1 for line in f)

    with open('/opt/ipv6kuma_v2/fullroute-check/old-route.txt',mode='r',encoding='utf-8') as f:
        yesterday_route = sum(1 for line in f)

    diff = today_route - yesterday_route

    # 経路数の増減に対するコメントを格納する
    if diff > 1:
        comment = '昨日と比べて{0}経路増えたクマ！！'.format(diff)
    elif diff == 0:
        comment = '昨日と比べて経路が増えていないクマ・・・'
    else:
        comment = '昨日と比べて{0}経路減ったクマ・・・'.format(abs(diff))

    
    d = datetime.datetime.today()
    today = d.strftime('%Y/%m/%d')
    post = '{0}の経路数は{1}だクマー。{2}'.format(today, today_route, comment)

    # 最新の経路数をグラフ元データファイルに追記する。
    update_data(today_route)

    return post

# ----------------------------------------------

def post_twitter(msg):
    '''
    msg変数をtwitterにPostする
    '''

    authcode = json.load(open('/opt/ipv6kuma_v2/twitter.json','r'))
    OAUTH_TOKEN = authcode[0]['oauth_token']
    OAUTH_SECRET =  authcode[0]['oauth_token_secret']
    CONSUMER_KEY = authcode[0]['consumer_key']
    CONSUMER_SECRET = authcode[0]['consumer_secret']

    t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_SECRET, CONSUMER_KEY, CONSUMER_SECRET))
    t.statuses.update(status = '{0}'.format(msg))

# ----------------------------------------------

def update_data(number):

    d = datetime.datetime.today()

    with open('/opt/ipv6kuma_v2/fullroute-check/sumGraph.txt',mode='a',encoding='utf-8') as f:
        f.write('{0}/{1}/{2},{3}\n'.format(d.year, d.month, d.day, number))

# ----------------------------------------------

def main():
    '''
    メイン処理
    '''
    # ipv6kuma格納ディレクトリを指定
    directory = '/opt/ipv6kuma_v2/fullroute-check'
    new = '{0}/new-route.txt'.format(directory)
    old = '{0}/old-route.txt'.format(directory)

    # 前日部分をバックアップする
    shutil.copyfile('{0}'.format(new),'{0}'.format(old))

    # wideから最新のフルルートを取得する
    attempt = 0
    while attempt < 3:
        try:
            get_fullroute_wide()
            break
        except UnicodeDecodeError:
            time.sleep(5)
            attempt = attempt + 1

    # ブイロクマのコメントを生成
    post = check_route()

    # TwitterにPost
    post_twitter(post)

# ----------------------------------------------

if __name__ == '__main__':
    main()
