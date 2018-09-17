#!/usr/bin/python3

import requests
import random
from bs4 import BeautifulSoup
import util


def get_steamcn_Invite():
    steamcn_url = 'https://steamcn.com/forum.php?mod=forumdisplay&fid=254&filter=typeid&typeid=495&orderby=dateline'
    headers = eval(open('steamcn_headers.json').read())

    util.take_break(random.randint(15, 30))

    r = requests.get(steamcn_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    table0 = soup.findAll('table')[0]
    tbodys = table0.findAll('tbody')
    aeles = []
    steamcn_invite = []
    count = 0

    while (count < 7):
        aele = tbodys[count].findAll('a')
        if len(aele):
            aeles.append('https://steamcn.com/' + aele[0].get('href'))
        count = count + 1

    for page_url in aeles:
        util.take_break(random.randint(15, 50))
        res = requests.get(page_url, headers=headers)
        page_soup = BeautifulSoup(res.text, "lxml")
        a_links = page_soup.findAll('a')
        if len(a_links):
            for link in a_links:
                link_url = link.get('href')
                if link_url is None:
                    pass
                elif 'www.steamgifts.com' in link_url:
                    print(link_url)
                    steamcn_invite.append(link_url)

    return steamcn_invite
