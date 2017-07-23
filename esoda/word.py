# -*- coding: utf-8 -*-
from .EsAdaptor import EsAdaptor
from .constant import defaultDB


def notstar(p, q):
    return p if p != '*' else q


def get_usage_list(t, i, dt, cids):
    usageList = []
    nt = list(t)
    ref = t[:]
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
            'colloc': '%s %s %s' % (t[i], t[i+1], dt),
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
                            'colloc': '%s %s %s' % (l1, l2, dt),
                            'count': j['doc_count']
                        })
                usageList += ret
            except Exception:
                logger.exception('In get_usage_list')
    return usageList
    
    
def get_usage3_list(t, i, dt, cids):
    usageList = []
    ref = t[:]

    if '*' not in t:
        cnt = EsAdaptor.count3(t, dt, defaultDB, cids, i)
        usageList.append({
            'ref': ' '.join(ref),
            'content': ' '.join(t),
            'colloc': '%s %s %s %s %s %s' % (t[0], t[1], t[2], dt[0], dt[1], i),
            'count': cnt['hits']['total']
        })
    else:
        lst = EsAdaptor.group3(t, dt, defaultDB, cids, i)
        starPos = [st for st, e in enumerate(t) if e == '*'][0]
        pat = ' '.join(['%s' if e == '*' else e for e in t])
        try:
            ret = []
            for j in lst['aggregations']['d']['d']['d']['buckets']:
                ref[starPos] = j['key']
                ret.append({
                    'ref': ' '.join(ref),
                    'content': pat % j['key'],
                    'colloc': '%s %s %s %s' % (pat % j['key'], dt[0], dt[1], i),
                    'count': j['doc_count']
                })
            usageList += ret
        except Exception:
            logger.exception('In get_usage3_list')
    return usageList