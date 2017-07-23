# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import User
import logging

from .utils import corpus_id2cids
from .youdao_query import youdao_suggest, youdao_translate
from .thesaurus import synonyms
from .lemmatizer import lemmatize
from .EsAdaptor import EsAdaptor
from .collocation import collocation_list, collocation3_list
from .word import get_usage_list, get_usage3_list
from .sentence import sentence_query, sentence3_query
from authentication.forms import FIELD_NAME
from common.models import Comment

defaultId = 11
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
    trans = youdao_translate(q0)
    q = trans['explanationList'][0][trans['explanationList'][0].find(']')+1:].strip() if trans['cn'] and trans['explanationList'] else q0
    qt, ref = lemmatize(q)

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

    r['collocationList'] = collocation3_list(qt, cids)

    if len(qt) == 1:
        r['synonymous'] = synonyms(qt[0])[:10]

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
    }

    request.session.save()
    logger.info('%s %s %s %s %s', request.META.get('REMOTE_ADDR', '0.0.0.0'), request, info, request.session.session_key, request.user)
    return render(request, 'esoda/result.html', info)


def sentence_view(request):
    t = request.GET.get('colloc', '').split()
    ref = request.GET.get('ref', '').split()
    i, dt = -1, []
    cids = get_cids(request.user.id)
    if len(t) == 6:
        i, dt, t = int(t[5]), t[3:5], t[:3]
    elif len(t) == 3:
        i, dt, t = 0, t[2], t[:2]
    if not t:
        t = request.GET.get('t', '').split()
    if not ref:
        ref = t
    
    sr = sentence3_query(t, ref, i, dt, cids)
    info = {
        'example_number': sr['total'],
        'search_time': sr['time'],
        'exampleList': sr['sentence']
    }
    return render(request, 'esoda/sentence_result.html', info)


def usagelist_view(request):
    t = request.GET.get('colloc', '').split()
    i, dt, r = -1, [], {}
    cids = get_cids(request.user.id)
    if len(t) == 6:
        i, dt, t = int(t[5]), t[3:5], t[:3]
        r = {'usageList': get_usage3_list(t, i, dt, cids)}
    elif len(t) == 3:
        i, dt, t = 0, t[2], t[:2]
        r = {'usageList': get_usage_list(t, i, dt, cids)}
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


