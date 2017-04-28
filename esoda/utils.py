from nltk.corpus import wordnet as WN
from .EsAdaptor import defaultCids, EsAdaptor
from .paper import mongo_get_object, mongo_get_object_or_404, DblpPaper, DblpVenue, UploadRecord
import requests


def synonymous(w):
    r = set()
    ss = WN.synsets(w)
    for s in ss:
        for l in s.lemmas():
            if '_' not in l.name():
                r.add(l.name())
    if w in r:
        r.remove(w)
    r = list(r)
    r.insert(0, w)
    # w is the first in results
    return tuple(r)


def is_cn_char(c):
    return 0x4e00 <= ord(c) < 0x9fa6


def is_cn(s):
    return reduce(lambda x, y: x and y, [is_cn_char(c) for c in s], True)


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


def gen_qt(q):
    tokens = q.split()
    return tokens[0] + ' ' + tokens[2]


def notstar(p, q):
    return p if p != '*' else q


def getUsageList(dt, cids=defaultCids):
    lst = EsAdaptor.group([], dt, cids)
    try:
        ret = []
        for i in lst['aggregations']['d']['d']['d']['buckets']:
            l1 = notstar(dt[0]['l1'], i['key'])
            l2 = notstar(dt[0]['l2'], i['key'])
            ret.append({
                'content': '%s...%s' % (l1, l2),
                'count': i['doc_count']
            })
        return ret
    except:
        return []


def paper_source_str(pid):
    s = {}
    p = mongo_get_object(DblpPaper, pk=pid)
    if not p:
        p = mongo_get_object_or_404(UploadRecord, pk=pid)
        s['source'] = 'Uploaded file: ' + p['title']
        return s
    # TODO: precompute source string and save to $common.uploads
    year = p['info'].get('year')
    title = p['info'].get('title', {}).get('text')
    authList = p['info'].get('authors', {}).get('author', [])

    source = ''
    v = mongo_get_object(DblpVenue, pk=p['venue'])
    if v:
        conference = v.get('shortName', v['fullName'])
        if year and len(year) == 4:
            conference += "'" + year[2:4]
        source += conference + '. '

        if authList:
            nameList = authList[0].split()  # split first author's name
            authorShort = nameList[0][0].upper() + '. ' +nameList[len(nameList) - 1]
            if len(authList) > 1:
                authorShort += ' et. al.'
            else:
                authorShort += '.'
            source += authorShort
        source += title
    return {'source': source, 'url': p['url']}
