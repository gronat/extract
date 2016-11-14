#!/usr/bin/python

import requests
from urllib import urlencode
from lxml import html
import re
import time
import random
import json
import random

def findAuthors(text):
    pattern = '([A-Z]\S+,(?: [A-Z]\.){1,3})'
    return re.findall(pattern, text)

def extractAuthors(lines):
    authors_list = []
    for text in lines:
        a = findAuthors(text)
        if len(a) > 0:
            authors_list.append(a)
    return authors_list

def poolAuthors(authors):
    s = set()
    for item in authors:
        for author in item:
            s.add(author)
    guys = list(s)
    guys.sort()
    return guys


def askScholar(author):

    URL = 'http://scholar.google.cz/scholar'
    headers = {
    'Host': 'scholar.google.cz',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    }

    query = {'q': author,
             'btnG' : '',
             'hl' : 'en',
             'as_std' : '0,5'
            }
    
    url = URL + "?" + urlencode(query).encode('ascii')
    response = requests.get(url, headers=headers, verify=False)
    return response



def findRecords(author):
    page = askScholar(author)
    if page.url.find('sorry') > -1:
        print page.url
        return None
    tree = html.fromstring(page.content)
    multiple = tree.xpath('//div[@class="gs_r"]//table//div[@style="padding:1px"]')
    single = tree.xpath('//div[@class="gs_r"]//table')
    pattern = r'(.*?) - (.*) - Cited by (.*)'

    records = []
    if len(multiple)>0:
        for item in multiple:
            text = item.text_content()
            groups = re.findall(pattern, text)[0]
            record = {'name' : groups[0], 'domain':groups[1], 'cited':int(groups[2])}
            records.append(record)
            
    elif len(single)>0:
        groups = single[0].xpath('tr/td//text()')
        record = {'name' : groups[1]+' '+groups[0], 'domain':groups[-2], 'cited':int(groups[-1].replace('Cited by ',''))}
        records.append(record)
        
    else:
        print 'Not found'
    return records

def printRecords(records):
    for r in records:
        print '%s\tcited by%d\t\t%s' % (r['name'], r['cited'], r['domain'])


if __name__ == '__main__':

    fname = 'citations.tex'

    lines = []
    with open(fname) as f:
        for line in f:
            if line != '\n':
                lines.append(line)

    
    authors_list = extractAuthors(lines)
    authors = poolAuthors(authors_list)
    random.shuffle(authors)
    # author = [
    #     'Obozinski, G.',
    #     'Li, P.',
    #     'Kantorov, V.',
    #     'Delaitre, V.',
    #     'Mikulik',
    #     'Laptev, I.',
    #     ]
    try:
        with open('scholar.json') as f:
            scholar = json.load(f)
        print '"scholar.json" found'
    except:
        scholar = {}
        print '"scholar.json" not found'

    for a in authors:
        print 'Fetching %s' % (a,)
        if a in scholar.keys():
            continue
        for _ in range(200):
            records = findRecords(a)
            if records is not None:
                printRecords(records)
                scholar[a] = records
                
                with open('scholar.json', 'w') as f:
                    json.dump(scholar,f)

                time.sleep(random.randint(60, 500))
                break
            else:
                msg = '%s\t Going to sleep (%s)\n' % (time.ctime(), a)
                with open('msg.log', 'wa') as f:
                        f.write(msg)
                print msg
                time.sleep(3600)

    print 'DONE'

