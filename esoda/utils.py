from django.conf import settings
from nltk.corpus import wordnet as WN
from .paper import mongo_get_object, mongo_get_objects, mongo_get_object_or_404, DblpPaper, DblpVenue, UploadRecord
import requests


def debug_object(o):
    print '<---- object -----'
    print '\n'.join(["%s:%s" % item for item in o.__dict__.items()])
    print '----- object ---->'


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


def corpus_id2cids(corpus_id):
    return [c['_id'] for c in settings.MONGODB['common']['corpora'].find({'field': corpus_id, 'status': 2})]


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


def gen_source_url(p, v):
    year = p['info'].get('year')
    title = p['info'].get('title', {}).get('text')
    authList = p['info'].get('authors', {}).get('author', [])
    source = ''
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


def paper_source_str(pid):
    s = {}
    p = mongo_get_object(DblpPaper, pk=pid)
    if not p:
        p = mongo_get_object_or_404(UploadRecord, pk=pid)
        s['source'] = 'Uploaded file: ' + p['title']
        return s
    # TODO: precompute source string and save to $common.uploads
    v = mongo_get_object(DblpVenue, pk=p['venue'])
    return gen_source_url(p, v)


def papers_source_str(pids):
    p = mongo_get_objects(DblpPaper, pks=pids)
    if not p:
        return {}
    # TODO: precompute source string and save to $common.uploads
    venues = [i['venue'] for i in p.values()]
    v = mongo_get_objects(DblpVenue, pks=venues)

    res = {}
    for i in pids:
        res[i] = gen_source_url(p[i], v[p[i]['venue']])
    return res
