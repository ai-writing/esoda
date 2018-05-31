# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
import logging
import time
import re
import json
import random

from .utils import *
from common.utils import timeit
from .youdao_query import youdao_suggest, suggest_new
if settings.DEBUG:
    from .youdao_query import youdao_translate_old as youdao_translate
else:
    from .youdao_query import youdao_translate_new as youdao_translate

from .thesaurus import synonyms
from .lemmatizer import lemmatize
from .EsAdaptor import EsAdaptor
from common.models import Comment
from authentication.models import TREE_FIRST, corpus_id2cids, FIELD_NAME


ALL_DEPS = [u'(主谓)', u'(动宾)', u'(修饰)', u'(介词)']
PERP_TOKENS = set(['vs', 're', 'contra', 'concerning', 'neath', 'skyward', 'another', 'near', 'howbeit', 'apropos', 'betwixt', 'alongside', 'amidst', 'outside', 'heavenward', 'notwithstanding', 'withal', 'epithetical', 'anent', 'continuously', 'transversely', 'amongst', 'circa', 'unto', 'aboard', 'about', 'above', 'across', 'after', 'against', 'along', 'amid', 'among', 'around', 'as', 'at', 'before', 'behind', 'below', 'beneath', 'beside', 'besides', 'between', 'beyond', 'but', 'by', 'despite', 'down', 'during', 'except', 'excepting', 'excluding', 'for', 'from', 'in', 'inside', 'into', 'like', 'of', 'off', 'on', 'onto', 'over', 'per', 'since', 'than', 'through', 'to', 'toward', 'towards', 'under', 'underneath', 'unlike', 'until', 'up', 'upon', 'versus', 'via', 'with', 'within', 'without',])
# ALL_DBS = ['dblp', 'doaj', 'bnc', 'arxiv']
# DEFAULT_ES_DBS = ['bnc', 'wikipedia'] # TODO: move into setting.py and .env
DEFAULT_ES_DBS = ['dblp'] # TODO: move into setting.py and .env
DEFAULT_ES_CIDS = ['conf_aaai', 'conf_acl', 'conf_asplos', 'conf_cav', 'conf_ccs', 'conf_chi', 'conf_cnhpca', 'conf_crypto', 'conf_cscw', 'conf_cvpr', 'conf_eurocrypt', 'conf_fast', 'conf_focs', 'conf_huc', 'conf_iccv', 'conf_icde', 'conf_icml', 'conf_icse', 'conf_ijcai', 'conf_infocom', 'conf_isca', 'conf_kbse', 'conf_kdd', 'conf_lics', 'conf_mm', 'conf_mobicom', 'conf_nips', 'conf_oopsla', 'conf_osdi', 'conf_pldi', 'conf_popl', 'conf_ppopp', 'conf_rtss', 'conf_sc', 'conf_sigcomm', 'conf_siggraph', 'conf_sigir', 'conf_sigmod', 'conf_sigsoft', 'conf_sosp', 'conf_sp', 'conf_stoc', 'conf_usenix', 'conf_uss', 'conf_visualization', 'conf_vldb', 'conf_www', 'journals_ai', 'journals_iandc', 'journals_ijcv', 'journals_ijmms', 'journals_jacm', 'journals_jmlr', 'journals_joc', 'journals_jsac', 'journals_pami', 'journals_pieee', 'journals_siamcomp', 'journals_tc', 'journals_tcad', 'journals_tdsc', 'journals_tifs', 'journals_tip', 'journals_tit', 'journals_tkde', 'journals_tmc', 'journals_tochi', 'journals_tocs', 'journals_tods', 'journals_tog', 'journals_tois', 'journals_ton', 'journals_toplas', 'journals_tos', 'journals_tosem', 'journals_tpds', 'journals_tse', 'journals_tvcg', 'journals_vldb', 'journals_micro', 'conf_vr',]
# DEFAULT_DOMAIN_NAME = u'通用英语'
DEFAULT_DOMAIN_NAME = u'计算机'
logger = logging.getLogger(__name__)

def get_cids(user):
    dbs, cids = [], []
    if user.is_authenticated and hasattr(user, 'userprofile'):  # TODO: create userprofile if none
        corpus_id = user.userprofile.getid()  # user.userprofile.getid() get a list
        dbs, cids = corpus_id2cids(corpus_id)
        # TODO: name = get_display_name(dbs, cids)
        name = u''
        count = 0
        for i in TREE_FIRST:
            if corpus_id[i] == 1:
                name = name + FIELD_NAME[count] + u','
            count += 1
        name = name[:-1]
    else:
        name = DEFAULT_DOMAIN_NAME

    dbs = dbs or DEFAULT_ES_DBS
    cids = cids or DEFAULT_ES_CIDS
    return dbs, cids, name


def get_feedback():
    info = {
        'comments': Comment.get_latest_comments(10),
        'count_of_favorite': 12049,
    }
    return info


@timeit
def esoda_view(request):
    q0 = request.GET.get('q', '').strip()

    # No query - render index.html
    if not q0:
        info = get_feedback()
        return render(request, 'esoda/index.html', info)

    # Ignore too long query
    # TODO: better user experience
    if len(q0.split()) > 20 or (has_cn(q0) and (len(q0.split()) + sum([1 for c in q0 if is_cn_char(c)])) > 20):
        info = get_feedback()
        logger.warning('User too long query: "%s"', q0)
        return render(request, 'esoda/index.html', info)

    # With query - render result.html
    q = q0
    if has_cn(q0):
        trans = youdao_translate(q0, timeout=5)
        if trans.get('explanationList'):
            try:
                q = trans['explanationList'][0][trans['explanationList'][0].find(']')+1:].strip()
            except Exception as e:
                logger.exception('Failed to parse youdao_translate result: "%s"', trans['explanationList'])

    q, ques, aste = refine_query(q) # ques(aste) is the place of question mark(asterisk)
    qt, ref, poss, dep = lemmatize(q, timeout=5)
    expand = []
    asteList = []
    for i in ques:
        expand.append(i)
    for i in aste:
        asteList.append(i)
    
    r = {
        # 'domain': u'人机交互',
        # 'phrase': [
        #     'improve quality',
        #     'standard quality',
        #     'best quality'
        # ],
        # 'commonColloc': [
        #     u'quality (主谓)*',
        #     u'quality (修饰)*',
        #     u'quality (介词)*'
        # ],
    }

    r['tlen'] = len(qt)
    dbs, cids, domain_name = get_cids(request.user)
    cL, cL_index = collocation_list(qt, ref, poss, dep, dbs, cids)
    r['collocationList'] = {'cL': cL, 'index': cL_index}

    # suggestion = {
    #     'relatedList': [
    #         'high quality',
    #         'improve quality',
    #         'ensure quality',
    #     ],
    #     'hotList': [
    #         'interaction',
    #         'algorithm',
    #         'application'
    #     ]
    # }

    info = {
        'r': r,
        'q': ' '.join(qt),
        'q0': q0,
        'ref': ' '.join(ref),
        'poss': ' '.join(poss),
        # 'suggestion': suggestion,
        # 'dictionary': trans,
        'dbs': dbs,
        # 'cids': cids,
        'expand': json.dumps(expand)
    }

    request.session.save()
    logger.info('%s %s %s %s %s %s', request.META.get('REMOTE_ADDR', '0.0.0.0'), request.session.session_key, request.user, request, info, domain_name)
    info['domain_name'] = domain_name
    return render(request, 'esoda/result.html', info)


def syn_usageList_view(request):
    # info = {
    #    'syn_usage_dict': {'word1':[{'ref': '', 'lemma': '', 'content': '', 'count': 10},……],'word2' ……}
    # }
    # TODO: add try...catch...
    t = request.GET.get('t', '').split()
    ref = request.GET.get('ref', '').split()
    expand = json.loads(request.GET.get('expand', '[]'))
    if not ref:
        ref = t
    dt = request.GET.get('dt', '0')
    dbs, cids, domain_name = get_cids(request.user)
    poss = request.GET.get('pos', '').split()
    dt = '0' if len(t) == 1 else dt   # TODO: deeply fix this bug
    usage_dict = get_usage_dict(t, ref, dt, dbs, cids)
    syn_dict = get_synonyms_dict(t, ref, dt, poss, dbs, cids)
    ttcnt = 0
    if dt != '0' and '*' not in t:
        d = [{'dt': dt, 'l1': t[0], 'l2': t[1]}]
        ttcnt = EsAdaptor.count([], d, dbs, cids)['hits']['total']
    else:
        ttcnt = EsAdaptor.count(t, [], dbs, cids)['hits']['total']

    t_list, star = star2collocation(t, dt)
    t_list0 = []
    if expand:
        for i in expand:
            t_list0.append(t_list[i])
        t_list = t_list0
    info = {
        't_list': t_list,
        'count': ttcnt,
        't_dt': (' '.join(t), dt),
        'ref': ' '.join(ref),
    }

    syn_usage_dict = {}
    count = 0
    displayed_t = []
    for i in xrange(len(t)):
        displayed_t.append(displayed_lemma(ref[i], t[i]))
        syn_usage_dict[displayed_lemma(ref[i], t[i])] = sort_syn_usageDict(syn_dict.get(t[i], []), usage_dict.get(t[i], []))
        if t[i] != '*':
            count += 1

    if '*' in t:
        syn_usage_dict[star] = syn_usage_dict['*']
        del syn_usage_dict['*']
        if usage_dict.get('*'):
            info['ref'] = usage_dict['*'][0]['ref']
            info['count'] = usage_dict['*'][0]['count']

    hint = 0
    # for k in t_list:
    #     for key in syn_usage_dict.keys():
    #         if k == key:
    #             if syn_usage_dict[key]:
    #                 if count != 1 or dt == '0' or k.encode('utf-8') in ['动词', '宾语', '介词', '修饰词', '被修饰词', '主语']:
    #                     hint += 1
    for key in syn_usage_dict.keys():
        hint = len(syn_usage_dict) if '*' not in syn_usage_dict.keys() else len(syn_usage_dict) - 1
    info['syn_usage_dict'] = refine_dep(syn_usage_dict, t, poss)
    info['hint'] = hint
    info['displayed_t'] = ' '.join(displayed_t)

    display_info = {
        't_list': info['t_list'],
        'count': info['count'],
        't_dt': info['t_dt'],
        'ref': info['ref'],
        'hint': info['hint'],
        'dbs': dbs,
    }

    logger.info('%s %s %s %s %s %s', request.META.get('REMOTE_ADDR', '0.0.0.0'), request.session.session_key, request.user, request, display_info, domain_name)
    return render(request, 'esoda/collocation_result.html', info)


def sentence_view(request):
    t = request.GET.get('t', '').split()
    ref = request.GET.get('ref', '').split()
    if not ref:
        ref = t
    i = int(request.GET.get('i', '0'))
    dt = request.GET.get('dt', '0')
    dep_count = request.GET.get('dep_count', '0')
    dbs, cids, domain_name = get_cids(request.user)
    if len(t) == 1:
        dt = '0'
    sr = sentence_query(t, ref, i, dt, dbs, cids)
    # for i in xrange(0, len(sr['sentence']), 10):
    #     temp = sr['sentence'][i:i+10]
    #     random.shuffle(temp)
    #     sr['sentence'][i:i+10] = temp
    info = {
        'example_number': len(sr['sentence']),
        'search_time': sr['time'],
        'exampleList': sr['sentence'],
        'similar_sen': abs(min(int(dep_count), 50) - len(sr['sentence'])),
        # TODO: sr['total'] unused
    }

    display_info = {
        'example_number': info['example_number'],
        'search_time': info['search_time'],
        'similar_sen': info['similar_sen'],
        'dbs': dbs,
    }

    logger.info('%s %s %s %s %s %s', request.META.get('REMOTE_ADDR', '0.0.0.0'), request.session.session_key, request.user, request, display_info, domain_name)
    return render(request, 'esoda/sentence_result.html', info)


def dict_suggest_view(request):
    q = request.GET.get('term', '')
    r = {'suggest': []}
    reMatch = re.compile(r'^[a-zA-Z0-9\s\'\-\.]*$')
    if reMatch.match(q):
        r = suggest_new(q)
    elif not has_cn(q):
        r = youdao_suggest(q)
    return JsonResponse(r)


@timeit
def get_collocations(clist, qt, ref, i, dbs, cids):
    # TODO: make clist as a return result
    try:
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
            flag = qt.index('*') if '*' in qt else -1
            clist.append({
                'type': pat % (qt[i], ALL_DEPS[j % 4], qt[i + 1]),
                'label': 'Colloc%d_%d' % (len(clist), j % 4 + 1),
                't_dt' : (list(qt), str(j % 4 + 1)),
                'count' : cnt,
                'flag': (flag, str(j % 4 + 1))
                # 'usageList': [],
            })
    except Exception as e:
        logger.exception('Failed in get_collocations: "%s"', ' '.join(qt))


@timeit
def collocation_list(t, ref, poss, dep, dbs, cids):
    # return collocation_list, default_collocation index
    # TODO: add try..catch...
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
    newlist, flag = get_defaulteColl(head, poss, dep, clist)
    return newlist, flag


@timeit
def get_usage_dict(t, ref, dt, dbs, cids):
    # TODO: add try...catch...
    i = 0 # 之前多个单词的query可以查询任意两个词之前的关系，i用来表示选中的单词的下标，现在多个单词不查找关系，所以i暂时不用，默认为0
    usageDict = {}
    for tt in t:
        usageDict[tt] = []
    if dt == '0' or len(t) > 2:
        return usageDict
    con = ''
    for k in (('*', t[i + 1]), (t[i], '*')):
        if k == ('*', '*'):
            continue
        try:
            d = [{'dt': dt, 'l1': k[0], 'l2': k[1]}]
            lst = EsAdaptor.group([], d, dbs, cids)
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
                        'lemma': '%s %s' % (l1, l2), # for query
                        'content': con, # for display
                        'count': j['doc_count'],
                        'type': 2 # for usageword
                    })
            if k[0] == '*':
                usageDict[t[i]] = ret
            else:
                usageDict[t[i + 1]] = ret
        except Exception:
            logger.exception('Failed in get_usage_list: "%s"', ' '.join(t))
    return usageDict


@timeit
def get_synonyms_dict(t, ref, dt, poss, dbs, cids):
    syn_dict = {}
    t_new = t[:]
    ref_new = ref[:]
    MAX_COUNT = 15  # TODO: deeply fix synonyms too many es queries bug
    req_head = {'index': dbs}

    if '*' in t:
        syn_dict['*'] = []
        t_new.remove('*')
        ref_new.remove('*')
    try:
        for j in xrange(len(t_new)):
            syn_list = []
            action = []
            pos = 'NONE' if len(t) == 1 else poss[j]
            for syn in synonyms(t_new[j], pos=pos, max_count=MAX_COUNT/len(t)):
                lemma = ' '.join(t_new).replace(t_new[j], syn)
                reff = ' '.join(ref_new).replace(ref_new[j], syn)
                if dt == '0' or len(t_new) == 1:
                    # cnt = EsAdaptor.count(lemma.split(' '), [], dbs, cids)['hits']['total']
                    req_body = EsAdaptor.get_action(lemma.split(' '), [], cids)
                else:
                    d = [{'dt': dt, 'l1': lemma.split(' ')[0], 'l2': lemma.split(' ')[1]}]
                    req_body = EsAdaptor.get_action([], d, cids)
                    # cnt = EsAdaptor.count([], d, dbs, cids)['hits']['total']
                # if cnt:
                action.extend([req_head, req_body])
                syn_list.append({'ref': reff, 'lemma': lemma, 'content': syn, 'type': 1, 'count': 0}) # type 1 for synonyms_word
            res = EsAdaptor.msearch(action)
            if len(syn_list) == len(res):
                for i in xrange(len(syn_list)):
                    syn_list[i]['count'] = res[i]['hits'].get('total')
            syn_dict[t_new[j]] = syn_list
    except Exception as e:
        logger.exception('Failed in get_synonyms_dict: "%s"', ' '.join(t))
    return syn_dict


@timeit
def sentence_query(t, ref, i, dt, dbs, cids):
    # TODO: remove i, which is negative & never used
    if not t:
        return {'time': 0.00, 'total': 0, 'sentence': []}
    if dt != '0':  # Search specific tag
        d = [{'dt': dt, 'i1': i, 'i2': i + 1}]
    else:  # Search user input
        d = []

    sr = {'time': 0, 'sentence': []}

    try:
        time1 = time.time()
        res = EsAdaptor.search(t, d, ref, dbs, cids, 50)    # TODO: set 50 as parameters, the same in rlen
        time2 = time.time()

        sr.update({'time': round(time2 - time1, 2), 'total': res['total']})
        rlen = min(50, len(res['hits']) if 'hits' in res else 0)

        papers = set()
        for i in xrange(rlen):
            papers.add(res['hits'][i]['_source']['p'].replace('_', '/'))
        sources = papers_source_str(list(papers))
        for i in xrange(rlen):
            sentence = res['hits'][i]
            sr['sentence'].append({
                'content': cleaned_sentence(sentence['fields']['sentence'][0]),
                'source': sources.get(sentence['_source']['p'].replace('_', '/'), {}),  # paper_source_str(sentence['_source']['p'])
                'heart_number': 129})
        sr = res_refine(sr)
    except Exception as e:
        logger.exception('Failed in sentence_query: "%s"', {'t': ' '.join(t), 'd': d})
    return sr
