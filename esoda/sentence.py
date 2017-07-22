# -*- coding: utf-8 -*-
from .EsAdaptor import EsAdaptor
from .constant import defaultDB
from .utils import papers_source_str

import time


def sentence3_query(t, ref, i, dt, cids):
    if not t:
        return {'time': 0.00, 'total': 0, 'sentence': []}
    if dt:  # Search specific tag
        if i == 0:
            d = [{'dt': dt[0], 'i1': 0, 'i2': 1}, {'dt': dt[1], 'i1': 1, 'i2': 2}]
        else:
            d = [{'dt': dt[0], 'i1': 0, 'i2': 2}, {'dt': dt[1], 'i1': 1, 'i2': 2}]
    else:  # Search user input
        d = []

    time1 = time.time()
    res = EsAdaptor.search3(t, d, ref, defaultDB, cids, 50)
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


def sentence_query(t, ref, i, dt, cids):
    if not t:
        return {'time': 0.00, 'total': 0, 'sentence': []}
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
