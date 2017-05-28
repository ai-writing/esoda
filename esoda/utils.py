# -*- coding: utf-8 -*-
from common.mongodb import MONGODB
from common.constant import CORPUS2ID, PUNCT_DICT
from .paper import mongo_get_object, mongo_get_objects, mongo_get_object_or_404, DblpPaper, UploadRecord
import requests
# import json


def debug_object(o):
    print '<---- object -----'
    print '\n'.join(["%s:%s" % item for item in o.__dict__.items()])
    print '----- object ---->'


def is_cn_char(c):
    return 0x4e00 <= ord(c) < 0x9fa6


def is_cn(s):
    return reduce(lambda x, y: x and y, [is_cn_char(c) for c in s], True)


def has_cn(s):
    return reduce(lambda x, y: x or y, [is_cn_char(c) for c in s], False)


def translate(cn):
    url = u'http://fanyi.youdao.com/openapi.do?keyfrom=ESLWriter&key=205873295&type=data&doctype=json&version=1.2&only=dict&q=' + cn
    l = ''
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            o = r.json()
            if o['errorCode'] == 0 and 'basic' in o and 'explains' in o['basic']:
                s = o['basic']['explains'][0]
                l = s[s.find(']') + 1:].strip()
    except Exception as e:
        print e
    return l


def corpus_id2cids(corpus_id):
    if corpus_id in CORPUS2ID:
        return [c['i'].replace('/', '_') for c in CORPUS2ID[corpus_id]]
    return [c['_id'].replace('/', '_') for c in MONGODB['dblp']['venues'].find({'field': corpus_id})]


def translate_cn(q):
    tokens = q.split()
    lent = len(tokens)
    qtt = []
    for i in xrange(lent):
        t = tokens[i]
        if is_cn(t):
            t = translate(t.strip('?'))
            # if not t:
            #     no translation for Chinese keyword
        qtt.append(t)
    st = ' '
    return st.join(qtt)


def notstar(p, q):
    return p if p != '*' else q


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


def paper_source_str(pid):
    s = {}
    p = mongo_get_object(DblpPaper, pk=pid)
    if not p:
        p = mongo_get_object_or_404(UploadRecord, pk=pid)
        s['source'] = 'Uploaded file: ' + p['title']
        return s
    # TODO: precompute source string and save to $common.uploads
    # v = mongo_get_object(DblpVenue, pk=p['venue'])
    return gen_source_url(p)


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


def cleaned_sentence(tokens, highlights):
    tt = [PUNCT_DICT.get(t, t) for t in tokens]
    for si in highlights:
        i = int(si)
        tt[i] = '<strong>%s</strong>' % tt[i]
    r = ' '.join(tt)
    r = r.replace(' \b', '')
    r = r.replace('\b ', '')
    r = r.replace(' <strong>\b', '<strong>')
    r = r.replace('\b</strong> ', '</strong>')
    return r
