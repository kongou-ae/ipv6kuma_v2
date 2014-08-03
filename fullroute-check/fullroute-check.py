#/usr/bin/python3.3
# -*- coding:utf-8 -*-

import requests
import re
import difflib


def get_fullroute():
    '''
    HE$B$N%9%J%C%W%7%g%C%H$r<hF@$7!"%Y%9%H%Q%9$r%U%!%$%k$K=q$-9~$`(B
    '''
    
    # HE$B$N%9%J%C%W%7%g%C%H$r<hF@(B
    html = requests.get('http://ipv6.he.net/bgpview/bgp-table-snapshot.txt')

    # $B<hF@$7$?%9%J%C%W%7%g%C%H$r%U%!%$%k$K=q$-9~$`(B
    with open('/opt/ipv6kuma_v2/fullroute-check/bgp-table-snapshot.txt',mode='w',encoding='utf-8') as f:
        f.write(html.content.decode('utf-8'))

    # $B=q$-9~$s$@%U%!%$%k$rFI$_9~$_!"@55,I=8=$G%Y%9%H%Q%9$rCj=P$7!"%U%!%$%k$K=q$-9~$`(B
    regex = re.compile(r'^\*>i([\da-zA-Z]{0,4}:)*\/\d{1,3}')
    newRoute = open('/opt/ipv6kuma_v2/fullroute-check/new-route.txt',mode='w',encoding='utf-8')
    with open('/opt/ipv6kuma_v2/fullroute-check/bgp-table-snapshot.txt',mode='r',encoding='utf-8') as f:
        for line in f:
            if regex.match(line):
                newRoute.write(regex.match(line).group() + '\n')

def main():
    '''
    $B%a%$%s=hM}(B
    '''
    get_fullroute()

if __name__ == '__main__':
    main()
