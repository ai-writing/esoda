# -*- coding: utf-8 -*-
from .EsAdaptor import EsAdaptor
from .constant import defaultDB


def notstar(p, q):
    return p if p != '*' else q


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
    
    
def get_usage3_list(t, ref, dt, cids, type):
    usageList = []

    if '*' not in t:
        cnt = EsAdaptor.count3(t, dt, defaultDB, cids, type)
        usageList.append({
            'ref': ' '.join(ref),
            'content': ' '.join(t),
            'count': cnt['hits']['total']
        })
    else:
        lst = EsAdaptor.group3(t, d, defaultDB, cids, type)
        starPos = [i for i, e in enumerate(t) if e == '*'][0]
        ref.insert(starPos, 0)
        t[starPos] = '%s'
        pat = ' '.join(t)
        try:
            ret = []
            for j in lst['aggregations']['d']['d']['d']['buckets']:
                ref[starPos] = j['key']
                ret.append({
                    'ref': ' '.join(ref),
                    'content': pat % j['key'],
                    'count': j['doc_count']
                })
            usageList += ret
        except Exception:
            logger.exception('In get_usage3_list')
    return usageList