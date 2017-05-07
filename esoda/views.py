# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User

import xml.sax
import json
import requests
import time

from .utils import translate_cn, notstar, papers_source_str, corpus_id2cids, debug_object
from authentication.forms import FIELDS
from .thesaurus import synonyms
from .lemmatizer import lemmatize
from .EsAdaptor import EsAdaptor

deps = [u'(主谓)', u'(动宾)', u'(修饰)', u'(介词)']
defaultCids = ["ecscw", "uist", "chi", "its", "iui", "hci", "ubicomp", "cscw", "acm_trans_comput_hum_interact_tochi_", "user_model_user_adapt_interact_umuai_", "int_j_hum_comput_stud_ijmms_", "mobile_hci"]


def esoda_view(request):
    q = request.GET.get('q', '').strip()

    # No query - render index.html
    if not q:
        info = {
            'feedbackList': [
                {
                    'content': u'无产阶级政党的党章是以马克思主义党的学说为指导，结合党的建设的实践而制定的党的生活准则和行为规范。',
                    'user_name': u'潘星宇'
                },
                {
                    'content': u'无产阶级政党的党章是以马克思主义党的学说为指导，结合党的建设的实践而制定的党的生活准则和行为规范。',
                    'user_name': u'潘星宇'
                }
            ],
            'count_of_favorite': 12049,
        }
        return render(request, 'esoda/index.html', info)

    # With query - render result.html
    q = translate_cn(q)

    r = {
        'domain': u'人机交互',
        'count': 222,
        'phrase': [
            'improve quality',
            'standard quality',
            'best quality'
        ],
        'commonColloc': [
            u'quality (主谓)*',
            u'quality (修饰)*',
            u'quality (介词)*'
        ],
        'collocationList': [
        ]
    }

    cids = defaultCids
    if request.user.id:
        user = User.objects.get(id=request.user.id)
        corpus_id = user.userprofile.corpus_id
        cids = corpus_id2cids(corpus_id)
        r['domain'] = FIELDS[corpus_id-1][1]

    qt = q.split()
    mqt = list(qt)
    r['collocationList'] = collocation_list(mqt, cids)

    if len(qt) == 1:
        syn = list(synonyms(q))
        if len(syn) > 10:
            syn = syn[0:10]
        r['synonymous'] = syn

    suggestion = {
        'relatedList': [
            'high quality',
            'improve quality',
            'ensure quality',
            '*(修饰) quality'
        ],
        'hotList': [
            'interaction',
            'algorithm',
            'application'
        ]
    }

    info = {
        'r': r,
        'q': q,
        'suggestion': suggestion,
    }

    YOUDAO_SEARCH_URL = 'http://dict.youdao.com/jsonapi?dicts={count:1,dicts:[[\"ec\"]]}&q=%s'
    jsonString = requests.get(YOUDAO_SEARCH_URL % q, timeout=10).text
    jsonObj = json.loads(jsonString.encode('utf-8'))

    if 'simple' in jsonObj and 'ec' in jsonObj:
        dictionary = {
            'word': q,
            'english': jsonObj['simple']['word'][0].get('ukphone', ''),
            'american': jsonObj['simple']['word'][0].get('usphone', ''),
            'explanationList': []
        }
        for explain in jsonObj['ec']['word'][0]['trs']:
            dictionary['explanationList'].append(explain['tr'][0]['l']['i'][0])
        info['dictionary'] = dictionary

    return render(request, 'esoda/result.html', info)


def sentence_view(request):
    q = request.GET.get('q', '')
    dtype = request.GET.get('dtype', '0')
    cids = defaultCids
    if request.user.id:
        user = User.objects.get(id=request.user.id)
        corpus_id = user.userprofile.corpus_id
        cids = corpus_id2cids(corpus_id)
    sr = sentence_query(q, dtype, cids)
    info = {
        'example_number': sr['total'],
        'search_time': sr['time'],
        'exampleList': sr['sentence']
    }
    return render(request, 'esoda/sentence_result.html', info)


class DictHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.suggest = []
        self.CurNum = 0
        self.CurTag = ''
        self.category = ''

    def startElement(self, tag, attributes):
        self.CurTag = tag
        if tag == 'item':
            self.suggest.append({})

    def endElement(self, tag):
        if tag == 'item':
            self.suggest[self.CurNum]['category'] = self.category
            self.category = ''
            self.CurNum += 1
        self.CurTag = ''

    def characters(self, content):
        if self.CurTag == 'title':
            self.suggest[self.CurNum]['label'] = content
            if content.find(' ') < 0:
                self.category = 'Words'
            else:
                self.category = 'Expressions'
        elif self.CurTag == 'explain':
            self.suggest[self.CurNum]['desc'] = content

YOUDAO_SUGGEST_URL = 'http://dict.youdao.com/suggest?ver=2.0&le=en&num=10&q=%s'


def dict_suggest_view(request):
    q = request.GET.get('term', '')
    r = {}
    try:
        xmlstring = requests.get(YOUDAO_SUGGEST_URL % q, timeout=10).text
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        Handler = DictHandler()
        xml.sax.parseString(xmlstring.encode('utf-8'), Handler)
        r['suggest'] = Handler.suggest
    except Exception as e:
        print repr(e)
    return JsonResponse(r)


def guide_view(request):
    info = {
    }
    return render(request, 'esoda/guide.html', info)


def get_usage_list(t, dt, cids, pat='%s...%s'):
    lst = EsAdaptor.group(t, dt, cids)
    try:
        ret = []
        for i in lst['aggregations']['d']['d']['d']['buckets']:
            l1 = notstar(dt[0]['l1'], i['key'])
            l2 = notstar(dt[0]['l2'], i['key'])
            ret.append({
                'content': pat % (l1, l2),
                'count': i['doc_count']
            })
        return ret
    except:
        return []

'''
def collocation_list_simple(mqt, cids):
    clist = []
    resList = EsAdaptor.collocation([], mqt, cids)
    if len(mqt) == 1:
        mqt.append('*')
    for i, p in enumerate(resList):
        if i == 4:
            mqt[0], mqt[1] = mqt[1], mqt[0]
        if not p:
            continue
        myTerm = {
            'type': u'%s %s %s' % (mqt[0], deps[i % 4], mqt[1]),
            'label': 'Colloc_%d' % (i + 1),
            'usageList': [],
        }
        for j in (('*', mqt[1]), (mqt[0], '*')):
            if j[0] != '*' or j[1] != '*':
                dt = [{'dt': i % 4 + 1, 'l1': j[0], 'l2': j[1]}]
                myTerm['usageList'] += get_usage_list((), dt, cids)
        if myTerm['usageList']:
            clist.append(myTerm)

    return clist
'''

def get_collocation(clist, qt, i, cids):
    t, d = list(qt), (qt[i], qt[i + 1])
    del t[i]
    del t[i]
    resList = EsAdaptor.collocation(t, d, cids)
    tx = list(t)
    tx.insert(i, '%s %s %s')
    pat1 = ' '.join(tx)
    tx[i] = '%s...%s'
    pat2 = ' '.join(tx)
    for j, p in enumerate(resList):
        if j == 4:
            qt[i], qt[i + 1] = qt[i + 1], qt[i]
        if not p:
            continue
        myTerm = {
            'type': pat1 % (qt[i], deps[j % 4], qt[i + 1]),
            'label': 'Colloc%d_%d' % (len(clist), j % 4 + 1),
            'usageList': [],
        }
        for k in (('*', qt[i + 1]), (qt[i], '*')):
            if k[0] != '*' or k[1] != '*':
                dt = [{'dt': j % 4 + 1, 'l1': k[0], 'l2': k[1]}]
                myTerm['usageList'] += get_usage_list(t, dt, cids, pat2)

        if myTerm['usageList']:
            clist.append(myTerm)


def collocation_list(mqt, cids):
    clist = []
    for i in range(len(mqt) - 1):
        get_collocation(clist, list(mqt), i, cids)
    for i in range(len(mqt)):
        qt = list(mqt)
        qt.insert(i, '*')
        get_collocation(clist, qt, i, cids)
    return clist


def sentence_query(q, dtype, cids=defaultCids):
    if dtype != '0':  # Search specific tag
        tq = q.split()[:-1]
        d = []
        for i in range(len(tq)):
            if '...' in tq[i]:
                ck = tq[i].split('...')
                tq[i] = ck[0]
                tq.insert(i+1, ck[1])
                d.append({'dt': dtype, 'i1': i, 'i2': i+1})
                break
        ll = ref = tq
    else:  # Search user input
        q = translate_cn(q)
        ll, ref = lemmatize(q)
        d = []

    time1 = time.time()
    res = EsAdaptor.search(ll, d, ref, cids, 50)
    time2 = time.time()

    sr = {'time': round(time2 - time1, 2), 'total': res['total'], 'sentence': []}
    rlen = min(50, len(res['hits']) if 'hits' in res else 0)

    papers = set()
    for i in xrange(rlen):
        papers.add(res['hits'][i]['_source']['p'])
    sources = papers_source_str(list(papers))
    for i in xrange(rlen):
        sentence = res['hits'][i]
        sr['sentence'].append({
            'content': sentence['fields']['sentence'][0],
            'source': sources.get(sentence['_source']['p'], {}),  # paper_source_str(sentence['_source']['p'])
            'heart_number': 129})
    return sr
