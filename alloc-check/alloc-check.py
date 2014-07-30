#!~/.virtualenvs/py3.3/bin/python
# -*- coding:utf-8 -*-

import requests
from bs4 import BeautifulSoup
import subprocess
import re
import shutil
import difflib
import time

# ----------------------------------------------

def get_jpnic_list():
    '''
    JPNICのリストを取得してファイルに書き込む
    '''

    html = requests.get('https://www.nic.ad.jp/ja/dns/ipv6-addr-block.html')
    soup = BeautifulSoup(html.content.decode('utf-8'))

    f = open('/opt/ipv6kuma_v2/alloc-check/new_jpnic.txt',mode='w',encoding='utf-8')
    for li in soup.find(id="blocks").find_all('li'):
        print(li.string, file=f)
    f.close

# ----------------------------------------------

def do_whois(prefix):
    '''
    引数をJPNIC WHOISに問い合わせ、組織名を戻す
    '''

    result = subprocess.Popen(['/bin/whois','-h','whois.nic.ad.jp','{0}/e'.format(prefix)], stdout=subprocess.PIPE).communicate()[0]

    regex = re.compile(b'\[Organization\]\s+(.+)')
    for i in regex.findall(result):
        return i.decode('utf-8')

# ----------------------------------------------

def diff_file(new,old):
    '''
    二つのファイルを受け取り、差分をSTRで戻す
    '''

    result = ''

    diff = subprocess.Popen(['/bin/diff','{0}'.format(new),'{0}'.format(old)], stdout=subprocess.PIPE).communicate()[0]

    regex = re.compile('<\s(.+)')
    for i in diff.decode('utf-8').splitlines():
        #print(i)
        for j in regex.findall(i):
            result += '{0}\n'.format(j)
    return result

# ----------------------------------------------

def main():
    ''' メイン処理 '''
    #ipv6kuma格納ディレクトリを指定
    directory = '/opt/ipv6kuma_v2/alloc-check'
    new = '{0}/new_jpnic.txt'.format(directory)
    old = '{0}/old_jpnic.txt'.format(directory)

    #前回のリストをバックアップする
    #shutil.copyfile('{0}/new_jpnic.txt'.format(directory),'{0}/old_jpnic.txt'.format(directory))

    #最新のリストを作成する
    get_jpnic_list()

    #リストを比較し、差分を作る。
    diff = diff_file('{0}'.format(new),'{0}'.format(old))
    for i in diff.splitlines():
        j = (do_whois(i))
        time.sleep(10)
        print("{0}が{1}を取得したクマー".format(j, i))


main()
