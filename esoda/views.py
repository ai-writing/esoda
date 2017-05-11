# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
from common.models import Comment
from datetime import datetime

import xml.sax
import json
import requests
import time

from .utils import translate_cn, notstar, papers_source_str, corpus_id2cids, debug_object
from authentication.forms import FIELD_NAME
from .thesaurus import synonyms
from .lemmatizer import lemmatize
from .EsAdaptor import EsAdaptor

deps = [u'(主谓)', u'(动宾)', u'(修饰)', u'(介词)']
defaultCids = ["ecscw", "uist", "chi", "its", "iui", "hci", "ubicomp", "cscw", "acm_trans_comput_hum_interact_tochi_", "user_model_user_adapt_interact_umuai_", "int_j_hum_comput_stud_ijmms_", "mobile_hci"]


def get_cids(rid, **kwargs):
    cids = defaultCids
    if rid:
        user = User.objects.get(id=rid)
        corpus_id = user.userprofile.corpus_id
        cids = corpus_id2cids(corpus_id)
        if 'r' in kwargs:
            kwargs['r']['domain'] = FIELD_NAME[corpus_id-1][1]  # TODO: translation
    return cids


def get_feedback():
    info = {
        'feedbackList': [
        ],
        'count_of_favorite': 12049,
    }
    for i in Comment.objects.all():
        if i.display:
            info['feedbackList'].append({
                'content': i.text,
                'user_name': i.user
            })
        if len(info['feedbackList']) == 10:
            break
    return info


def esoda_view(request):
    q = request.GET.get('q', '').strip()

    # No query - render index.html
    if not q:
        info = get_feedback()
        return render(request, 'esoda/index.html', info)

    # With query - render result.html
    q0 = q
    q = translate_cn(q)

    r = {
        'domain': u'人机交互',
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

    cids = get_cids(request.user.id, r=r)

    qt, ref = lemmatize(q)
    mqt = list(qt)
    r['collocationList'] = collocation_list(mqt, cids)

    if len(qt) == 1:
        syn = list(synonyms(qt[0]))
        if len(syn) > 10:
            syn = syn[0:10]
        r['synonymous'] = syn

    suggestion = {
        'relatedList': [
            'high quality',
            'improve quality',
            'ensure quality',
        ],
        'hotList': [
            'interaction',
            'algorithm',
            'application'
        ]
    }

    qt = ' '.join(qt)
    ref = ' '.join(ref)
    info = {
        'r': r,
        'q': qt,
        'q0': q0,
        'ref': ref,
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

def message_view(request):
    message = request.POST.get('message','')
    if request.user.id:
        user = User.objects.get(id=request.user.id)
        c = Comment(text=message, user=user, display=True, date=datetime.now())
        c.save()
    info = get_feedback()
    return render(request, 'esoda/index.html', info)

def sentence_view(request):
    t = request.GET.get('t', '').split()
    ref = request.GET.get('ref', '').split()
    if not ref:
        ref = t
    i = int(request.GET.get('i', '0'))
    dt = request.GET.get('dt', '0')
    cids = get_cids(request.user.id)
    sr = sentence_query(t, ref, i, dt, cids)
    info = {
        'example_number': sr['total'],
        'search_time': sr['time'],
        'exampleList': sr['sentence']
    }
    return render(request, 'esoda/sentence_result.html', info)


def usagelist_view(request):
    t = request.GET.get('t', '').split()
    ref = request.GET.get('ref', '').split()
    if not ref:
        ref = t
    i = int(request.GET.get('i', '0'))
    dt = request.GET.get('dt', '0')
    cids = get_cids(request.user.id)
    r = {'usageList': get_usage_list(t, ref, i, dt, cids)}
    return render(request, 'esoda/collocation_result.html', r)


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


def get_usage_list(t, ref, i, dt, cids):
    usageList = []
    nt = list(t)
    del nt[i]
    del nt[i]
    nnt = list(nt)
    nnt.insert(i, '%s...%s')
    pat = ' '.join(nnt)

    if '*' not in t:
        d = [{'dt': dt, 'l1': t[i], 'l2': t[i + 1]}]
        cnt = EsAdaptor.count(nt, d, cids)
        usageList.append({
            'ref': ' '.join(ref),
            'content': pat % (t[i], t[i + 1]),
            'count': cnt['hits']['total']
        })
    for k in (('*', t[i + 1]), (t[i], '*')):
        if k[0] != '*' or k[1] != '*':
            d = [{'dt': dt, 'l1': k[0], 'l2': k[1]}]

            lst = EsAdaptor.group(nt, d, cids)
            try:
                ret = []
                for j in lst['aggregations']['d']['d']['d']['buckets']:
                    l1 = notstar(d[0]['l1'], j['key'])
                    l2 = notstar(d[0]['l2'], j['key'])
                    if (l1, l2) != (t[i], t[i+1]):
                        nref = list(ref)
                        if l1 != t[i]:
                            nref[i] = l1
                        else:
                            nref[i+1] = l2
                        ret.append({
                            'ref': ' '.join(nref),
                            'content': pat % (l1, l2),
                            'count': j['doc_count']
                        })
                usageList += ret
            except Exception as e:
                print repr(e)
    return usageList


def get_collocations(clist, qt, i, cids):
    t, d = list(qt), (qt[i], qt[i + 1])
    del t[i]
    del t[i]
    resList = EsAdaptor.collocation(t, d, cids)
    t = list(t)
    t.insert(i, '%s %s %s')
    pat = ' '.join(t)
    for j, p in enumerate(resList):
        if j == 4:
            qt[i], qt[i + 1] = qt[i + 1], qt[i]
        if not p:
            continue
        clist.append({
            'type': pat % (qt[i], deps[j % 4], qt[i + 1]),
            'label': 'Colloc%d_%d' % (len(clist), j % 4 + 1),
            # 'usageList': [],
        })

def collocation_list(mqt, cids):
    clist = []
    if len(mqt) == 1:
        mqt.append('*')
    for i in range(len(mqt) - 1):
        get_collocations(clist, list(mqt), i, cids)
    '''
    for i in range(len(mqt)):
        qt = list(mqt)
        qt.insert(i, '*')
        get_collocation(clist, qt, i, cids)
    '''
    return clist


def sentence_query(t, ref, i, dt, cids):
    if dt != '0':  # Search specific tag
        d = [{'dt': dt, 'i1': i, 'i2': i+1}]
    else:  # Search user input
        t = ' '.join(t)
        t, ref = lemmatize(t)
        d = []

    time1 = time.time()
    res = EsAdaptor.search(t, d, ref, cids, 50)
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
