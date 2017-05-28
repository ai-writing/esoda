# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
import logging

import time

from .utils import translate_cn, notstar, papers_source_str, corpus_id2cids
from .usage import process_usage_list, process_sentence_list, process_usage_usage_list
from .youdao_query import youdao_suggest, youdao_search
from .thesaurus import synonyms
from .lemmatizer import lemmatize
from .EsAdaptor import EsAdaptor
from authentication.forms import FIELD_NAME
from common.models import Comment


deps = [u'(主谓)', u'(动宾)', u'(修饰)', u'(介词)']
defaultId = 11
defaultDB = '_all'
logger = logging.getLogger(__name__)


def get_cids(rid, **kwargs):
    if rid:
        user = User.objects.get(id=rid)
        corpus_id = user.userprofile.corpus_id
    else:
        corpus_id = defaultId
    cids = corpus_id2cids(str(corpus_id))
    if 'r' in kwargs:
        p = [i[1] for i in FIELD_NAME if i[0] == corpus_id]
        kwargs['r']['domain'] = p[0] if p else '其它'
    return cids


def get_feedback():
    info = {
        'comments': Comment.get_latest_comments(10),
        'count_of_favorite': 12049,
    }
    return info


def esoda_view(request):
    q0 = request.GET.get('q', '').strip()

    # No query - render index.html
    if not q0:
        info = get_feedback()
        return render(request, 'esoda/index.html', info)

    # With query - render result.html
    q = translate_cn(q0)

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
        ],
        'usageList': [
        ]
    }

    cids = get_cids(request.user.id, r=r)

    qt, ref = lemmatize(q)
    r['collocationList'] = collocation_list(qt, cids)
    r['usageList'] = process_usage_list(qt)

    if len(qt) == 1:
        syn = synonyms(qt[0])
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

    info = {
        'r': r,
        'q': ' '.join(qt),
        'q0': q0,
        'ref': ' '.join(ref),
        'suggestion': suggestion,
        'dictionary': youdao_search(q0, ' '.join(qt)),
        'cids': cids,
    }

    logger.info('%s %s', request, info)
    return render(request, 'esoda/result.html', info)


def usage_sentence_view(request):
    md = request.GET.get('t', '')
    t = md.split()
    sr = process_sentence_list(t, md)
    info = {
        'example_number': sr['total'],
        'search_time': sr['time'],
        'exampleList': sr['sentence']
    }
    return render(request, 'esoda/sentence_result.html', info)


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


def usage_view(request):
    md = request.GET.get('t', '')
    t = md.split()
    r = {'usageList': process_usage_usage_list(t, md)}
    return render(request, 'esoda/usage_result.html', r)


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


def dict_suggest_view(request):
    q = request.GET.get('term', '')
    r = {}
    try:
        r = youdao_suggest(q)
    except Exception:
        logger.exception('Failed to parse Youdao suggest')
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
        cnt = EsAdaptor.count(nt, d, defaultDB, cids)
        usageList.append({
            'ref': ' '.join(ref),
            'content': pat % (t[i], t[i + 1]),
            'count': cnt['hits']['total']
        })
    for k in (('*', t[i + 1]), (t[i], '*')):
        if k[0] != '*' or k[1] != '*':
            d = [{'dt': dt, 'l1': k[0], 'l2': k[1]}]

            lst = EsAdaptor.group(nt, d, defaultDB, cids)
            try:
                ret = []
                for j in lst['aggregations']['d']['d']['d']['buckets']:
                    l1 = notstar(d[0]['l1'], j['key'])
                    l2 = notstar(d[0]['l2'], j['key'])
                    if (l1, l2) != (t[i], t[i + 1]):
                        nref = list(ref)
                        if l1 != t[i]:
                            nref[i] = l1
                        else:
                            nref[i + 1] = l2
                        ret.append({
                            'ref': ' '.join(nref),
                            'content': pat % (l1, l2),
                            'count': j['doc_count']
                        })
                usageList += ret
            except Exception:
                logger.exception('In get_usage_list')
    return usageList


def get_collocations(clist, qt, i, cids):
    t, d = list(qt), (qt[i], qt[i + 1])
    del t[i]
    del t[i]
    resList = EsAdaptor.collocation(t, d, defaultDB, cids)
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
    mqt = list(mqt)
    clist = []
    if len(mqt) == 1:
        mqt.append('*')
    for i in range(len(mqt) - 1):
        get_collocations(clist, mqt, i, cids)
    '''
    for i in range(len(mqt)):
        qt = list(mqt)
        qt.insert(i, '*')
        get_collocation(clist, qt, i, cids)
    '''
    return clist


def sentence_query(t, ref, i, dt, cids):
    if dt != '0':  # Search specific tag
        d = [{'dt': dt, 'i1': i, 'i2': i + 1}]
    else:  # Search user input
        d = []

    time1 = time.time()
    res = EsAdaptor.search(t, d, ref, defaultDB, cids, 50)
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
