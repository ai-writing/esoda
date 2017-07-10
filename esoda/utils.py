# -*- coding: utf-8 -*-
from .paper import mongo_get_objects, DblpPaper
from .constant import CORPUS2ID
import requests
import json


def debug_object(o):
    print '<---- object -----'
    print '\n'.join(["%s:%s" % item for item in o.__dict__.items()])
    print '----- object ---->'


def is_cn_char(c):
    return 0x4e00 <= ord(c) < 0x9fa6


def has_cn(s):
    return reduce(lambda x, y: x or y, [is_cn_char(c) for c in s], False)


def corpus_id2cids(corpus_id):
    return [c['i'].replace('/', '_') for c in CORPUS2ID.get(corpus_id, [])]


def generate_source(year, title, authList, conference):
    source = ''
    # assert: should always be this case
    conference += "'" + str(year % 100)
    source += conference + '. '

    if authList:
        nameList = authList[0].split()  # split first author's name
        authorShort = nameList[0][0].upper() + '. ' +nameList[len(nameList) - 1]
        if len(authList) > 1:
            authorShort += ' et. al.'
        else:
            authorShort += '.'
        source += authorShort
    source += ' ' + title
    return source


def gen_source_url(p):
    year = int(p.get('year'))
    title = p.get('title', '')
    authList = p.get('authors', '').split(';')
    conference = p.get('venue', '/').split('/')[-1].upper()
    source = generate_source(year, title, authList, conference)
    return {'source': source, 'url': p['ee']}


def papers_source_str(pids):
    p = mongo_get_objects(DblpPaper, pks=pids)
    if not p:
        return {}
    # TODO: precompute source string and save to $common.uploads
    # venues = [i['venue'] for i in p.values()]
    # v = mongo_get_objects(DblpVenue, pks=venues)

    res = {}
    for i in pids:
        if i in p:
            res[i] = gen_source_url(p[i])
    return res
