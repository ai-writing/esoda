# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
import logging
import time
import re

from .utils import *
from .youdao_query import youdao_suggest, suggest_new
if settings.DEBUG:
    from .youdao_query import youdao_translate_old as youdao_translate
else:
    from .youdao_query import youdao_translate_new as youdao_translate

from .thesaurus import synonyms
from .lemmatizer import lemmatize
from .EsAdaptor import EsAdaptor
from .utils import FIELD_NAME
from common.models import Comment
from authentication.views import tree_first
from common.mongodb import MONGODB


ALL_DEPS = [u'(主谓)', u'(动宾)', u'(修饰)', u'(介词)']
PERP_TOKENS = [r['_id'] for r in MONGODB.common.prep_tokens.find()]
# ALL_DBS = ['dblp', 'doaj', 'bnc', 'arxiv']
DEFAULT_DBS = ['dblp']
DEFAULT_CIDS = ['_all']
logger = logging.getLogger(__name__)

def get_cids(user, r=None):
    dbs, cids = [], []
    if user.is_authenticated:
        corpus_id = user.userprofile.getid()  # user.userprofile.getid() get a list
        dbs, cids = corpus_id2cids(corpus_id)
        # TODO: name = get_name(dbs, cids)
        name = u''
        count = 0
        for i in tree_first:
            if corpus_id[i] == 1:
                name = name + FIELD_NAME[count] + u', '
            count += 1
        name = name[0:-2]
    else:
        name = u'计算机全部领域'
    if r:
        r['domain'] = name
    dbs = dbs or DEFAULT_DBS
    cids = cids or DEFAULT_CIDS
    return dbs, cids


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
    trans = youdao_translate(q0)
    q = trans['explanationList'][0][trans['explanationList'][0].find(']')+1:].strip() if trans['cn'] and trans['explanationList'] else q0
    expand = get_expand(q)
    expand_str = ''
    for item in expand:
        qt, ref, poss, dep = lemmatize(item)
        expand_str += qt[0] + ' '
    logger.info("before refine: %s", expand_str)
    q = refine_query(q)
    qt, ref, poss, dep = lemmatize(q)
    
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

    dbs, cids = get_cids(request.user, r=r)
    r['tlen'] = len(qt)
    cL, cL_index = collocation_list(qt, ref, poss, dep, dbs, cids)
    r['collocationList'] = {'cL': cL, 'index': cL_index}

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
        'dictionary': trans,
        'cids': cids,
        'expand': expand_str
    }

    request.session.save()
    logger.info('%s %s %s %s %s', request.META.get('REMOTE_ADDR', '0.0.0.0'), request.session.session_key, request.user, request, info)
    return render(request, 'esoda/result.html', info)


def get_synonyms_dict(t, ref, i, dt, dbs, cids):
    syn_dict = {}
    t_new = t[:]
    ref_new = ref[:]
    if '*' in t:
        syn_dict['*'] = []
        t_new.remove('*')
        ref_new.remove('*')
    for tt in t_new:
        syn_dict[tt] = []
        for syn in synonyms(tt)[:6]:
            lemma = ' '.join(t_new).replace(tt, syn[0])
            reff = ' '.join(ref_new).replace(tt, syn[0])
            if dt == '0' or len(t_new) == 1:
                cnt = EsAdaptor.count(lemma.split(' '), [], dbs, cids)['hits']['total']
            else:
                d = [{'dt': dt, 'l1': lemma.split(' ')[0], 'l2': lemma.split(' ')[1]}]
                cnt = EsAdaptor.count([], d, dbs, cids)['hits']['total']
            if cnt:
                syn_dict[tt].append({'ref': reff, 'lemma': lemma, 'content': syn[0], 'count': cnt, 'type': 1, 'weight': syn[1]}) # type 1 for synonyms_word
    return syn_dict


def syn_usageList_view(request):
    # info = {
    #    'syn_usage_dict': {'word1':[{'ref': '', 'lemma': '', 'content': '', 'count': 10},……],'word2' ……}
    # }
    t = request.GET.get('t', '').split()
    ref = request.GET.get('ref', '').split()
    expand_str = request.GET.get('expand', '')
    if expand_str:
        expand_exist = True
    else:
        expand_exist = False
    expand_list = expand_str.split()
    if not ref:
        ref = t
    i = int(request.GET.get('i', '0'))
    dt = request.GET.get('dt', '0')
    dbs, cids = get_cids(request.user)
    usage_dict = get_usage_dict(t, ref, i, dt, dbs, cids)
    syn_dict = get_synonyms_dict(t, ref, i, dt, dbs, cids)

    ttcnt = 0
    if dt != '0' and '*' not in t:
        d = [{'dt': dt, 'l1': t[i], 'l2': t[i + 1]}]
        ttcnt = EsAdaptor.count([], d, dbs, cids)['hits']['total']
    else:
        ttcnt = EsAdaptor.count(t, [], dbs, cids)['hits']['total']

    t_list, star = star2collocation(t, dt)
    t_str = ' '.join(t)
    info = {
        't_list': t_list,
        'count': ttcnt,
        'type': ' '.join(t_list),
        'syn_dict': {},
        't_dt': (' '.join(t), dt),
        'expand_exist': expand_exist,
        'expand': expand_list,
    }

    syn_usage_dict = {}
    for tt in t:
        syn_usage_dict[tt] = sort_syn_usageDict(syn_dict[tt], usage_dict[tt])

    if '*' in t:
        syn_usage_dict[star] = syn_usage_dict['*']
        t_str = t_str.strip('* ')

    info['t_str'] = t_str
    info['syn_usage_dict'] = syn_usage_dict
    return render(request, 'esoda/collocation_result.html', info)


def sentence_view(request):
    t = request.GET.get('t', '').split()
    ref = request.GET.get('ref', '').split()
    if not ref:
        ref = t
    i = int(request.GET.get('i', '0'))
    dt = request.GET.get('dt', '0')
    dbs, cids = get_cids(request.user)
    if len(t) == 1:
        dt = '0'
    sr = sentence_query(t, ref, i, dt, dbs, cids)
    info = {
        'example_number': len(sr['sentence']),
        'search_time': sr['time'],
        'exampleList': sr['sentence']
    }
    return render(request, 'esoda/sentence_result.html', info)


# def usagelist_view(request):
#     t = request.GET.get('t', '').split()
#     ref = request.GET.get('ref', '').split()
#     if not ref:
#         ref = t
#     i = int(request.GET.get('i', '0'))
#     dt = request.GET.get('dt', '0')
#     dbs, cids = get_cids(request.user)
#     r = {'usageList': get_usage_list(t, ref, i, dt, dbs, cids)}
#     return render(request, 'esoda/collocation_result.html', r)


def dict_suggest_view(request):
    q = request.GET.get('term', '')
    r = {}
    reMatch = re.compile('^[a-zA-Z0-9\s\'\-\.]*$')
    if reMatch.match(q):
        r = suggest_new(q)
    else:
        r = youdao_suggest(q)
    return JsonResponse(r)


def guide_view(request):
    info = {
    }
    return render(request, 'esoda/guide.html', info)


def get_usage_dict(t, ref, i, dt, dbs, cids):
    usageDict = {}
    nt = list(t)
    for tt in t:
        usageDict[tt] = []
    if dt == '0':
        return usageDict
    del nt[i]
    del nt[i]
    nnt = list(nt)
    nnt.insert(i, '%s %s')
    pat = ' '.join(nnt)

    # if '*' not in t:
    #     d = [{'dt': dt, 'l1': t[i], 'l2': t[i + 1]}]
    #     cnt = EsAdaptor.count(nt, d, dbs, cids)
    #     usageList.append({
    #         'ref': ' '.join(ref),
    #         'lemma': pat % (t[i], t[i + 1]),
    #         'content': pat % (displayed_lemma(ref[i], t[i]), displayed_lemma(ref[i + 1], t[i + 1])),
    #         'count': cnt['hits']['total']
    #     })
    con = ''
    for k in (('*', t[i + 1]), (t[i], '*')):
        d = [{'dt': dt, 'l1': k[0], 'l2': k[1]}]
        lst = EsAdaptor.group(nt, d, dbs, cids)
        try:
            ret = []
            for j in lst['aggregations']['d']['d']['d']['buckets']:
                l1 = notstar(d[0]['l1'], j['key'])
                l2 = notstar(d[0]['l2'], j['key'])
                t1 = [l1 if d[0]['l1'] == '*' else displayed_lemma(ref[i], k[0])]
                t2 = [l2 if d[0]['l2'] == '*' else displayed_lemma(ref[i + 1], k[1])]
                if (l1, l2) != (t[i], t[i + 1]):
                    nref = list(ref)
                    if l1 != t[i]:
                        con = l1
                        nref[i] = l1
                    else:
                        con = l2
                        nref[i + 1] = l2
                    ret.append({
                        'ref': ' '.join(nref),
                        'lemma': pat % (l1, l2), # for query
                        'content': con, # for display
                        'count': j['doc_count'],
                        'type': 2 # for usageword
                    })
            if k[0] == '*':
                usageDict[t[i]] = ret
            else:
                usageDict[t[i+1]] = ret
        except Exception:
            logger.exception('In get_usage_list')
    return usageDict


def get_collocations(clist, qt, ref, i, dbs, cids):
    t, d = list(qt), (qt[i], qt[i + 1])
    cnt = 0
    del t[i]
    del t[i]
    resList = EsAdaptor.collocation(t, d, dbs, cids)
    nt = list(t)
    t.insert(i, '%s %s %s')
    pat = ' '.join(t)
    for j, p in enumerate(resList):
        if j == 4:
            qt[i], qt[i + 1] = qt[i + 1], qt[i]
        if not p:
            continue
        if '*' in qt:
            dd = []
            cnt = 10 # one word query set a default number of coll
        else:
            dd = [{'dt': j % 4 + 1, 'l1': qt[i], 'l2': qt[i + 1]}]
            cnt = EsAdaptor.count(nt, dd, dbs, cids)['hits']['total']
        clist.append({
            'type': pat % (qt[i], ALL_DEPS[j % 4], qt[i + 1]),
            'label': 'Colloc%d_%d' % (len(clist), j % 4 + 1),
            't_dt' : (list(qt), str(j % 4 + 1)),
            'count' : cnt
            # 'usageList': [],
        })


def collocation_list(t, ref, poss, dep, dbs, cids):
    # return collocation_list, default_collocation index
    cnt = EsAdaptor.count(t, [], dbs, cids)['hits']['total']
    head = [{'count': cnt, 't_dt': (t, '0'), 'type': ' '.join(t), 'label':  'Colloc0_0', 'title': u'全部结果'}] # all results
    clist = []
    if len(t) >= 3:
        return head, 1
    if len(t) == 1:
        if t[0] in PERP_TOKENS:
            return head, 1
        t.append('*')
        ref.append('*')
    for i in range(len(t) - 1):
        get_collocations(clist, t, ref, i, dbs, cids)
    newlist, flag = get_defaulteColl(head, dep, clist)
    return newlist, flag


def sentence_query(t, ref, i, dt, dbs, cids):
    if not t:
        return {'time': 0.00, 'total': 0, 'sentence': []}
    if dt != '0':  # Search specific tag
        d = [{'dt': dt, 'i1': i, 'i2': i + 1}]
    else:  # Search user input
        d = []

    time1 = time.time()
    res = EsAdaptor.search(t, d, ref, dbs, cids, 50)
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
            'content': cleaned_sentence(sentence['fields']['sentence'][0]),
            'source': sources.get(sentence['_source']['p'], {}),  # paper_source_str(sentence['_source']['p'])
            'heart_number': 129})
    sr = res_refine(sr)
    return sr


def refresh_synList(t, syn_list, index, dt, dbs, cids):
    # return a synonymous_list of every word
    synonymous_list = []
    for syn in syn_list:
        t_syn = (t, syn) if index == 1 else (syn, t)
        d = [{'dt': dt, 'l1': t_syn[0], 'l2': t_syn[1]}]
        cnt = EsAdaptor.count([], d, dbs, cids)['hits']['total']
        if cnt != 0:
            synonymous_list.append({'ref': ' '.join(t_syn), 'lemma': ' '.join(t_syn), 'content': syn, 'count': cnt})
    return synonymous_list
