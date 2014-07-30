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
    JPNIC$B$N%j%9%H$r<hF@$7$F%U%!%$%k$K=q$-9~$`(B
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
    $B0z?t$r(BJPNIC WHOIS$B$KLd$$9g$o$;!"AH?%L>$rLa$9(B
    '''

    result = subprocess.Popen(['/bin/whois','-h','whois.nic.ad.jp','{0}/e'.format(prefix)], stdout=subprocess.PIPE).communicate()[0]

    regex = re.compile(b'\[Organization\]\s+(.+)')
    for i in regex.findall(result):
        return i.decode('utf-8')

# ----------------------------------------------

def diff_file(new,old):
    '''
    $BFs$D$N%U%!%$%k$r<u$1<h$j!":9J,$r(BSTR$B$GLa$9(B
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
    ''' $B%a%$%s=hM}(B '''
    #ipv6kuma$B3JG<%G%#%l%/%H%j$r;XDj(B
    directory = '/opt/ipv6kuma_v2/alloc-check'
    new = '{0}/new_jpnic.txt'.format(directory)
    old = '{0}/old_jpnic.txt'.format(directory)

    #$BA02s$N%j%9%H$r%P%C%/%"%C%W$9$k(B
    #shutil.copyfile('{0}/new_jpnic.txt'.format(directory),'{0}/old_jpnic.txt'.format(directory))

    #$B:G?7$N%j%9%H$r:n@.$9$k(B
    get_jpnic_list()

    #$B%j%9%H$rHf3S$7!":9J,$r:n$k!#(B
    diff = diff_file('{0}'.format(new),'{0}'.format(old))
    for i in diff.splitlines():
        j = (do_whois(i))
        time.sleep(10)
        print("{0}$B$,(B{1}$B$r<hF@$7$?%/%^!<(B".format(j, i))


main()
