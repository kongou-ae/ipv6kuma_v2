#/usr/bin/python3.3
# -*- coding:utf-8 -*-

import requests
import re
import difflib


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

def main():
    '''
    メイン処理
    '''
    get_fullroute()

if __name__ == '__main__':
    main()
