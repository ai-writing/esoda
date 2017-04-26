from nltk.corpus import wordnet as WN

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
    return reduce(lambda x,y: x and y, [is_cn_char(c) for c in s], True)

def translate(cn):
    url = u'http://fanyi.youdao.com/openapi.do?keyfrom=ESLWriter&key=205873295&type=data&doctype=json&version=1.2&only=dict&q=' + cn
    l = ''
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            o = r.json()
            if o['errorCode'] == 0 and 'basic' in o and 'explains' in o['basic']:
                s = o['basic']['explains'][0]
                l = s[s.find(']')+1:].strip()
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
                # no translation for Chinese keyword
        qtt.append(t)
    st = ' '
    return st.join(qtt)

def gen_qt(q):
    tokens = q.split()
    return tokens[0] + ' ' + tokens[2]
