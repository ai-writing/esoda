# -*- coding: utf-8 -*-
from .EsAdaptor import EsAdaptor
from itertools import permutations
from .constant import deps, defaultDB


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


colloc3 = [(0, 1), (0, 3), (1, 3), (2, 0), (2, 1), (2, 3), (3, 3)]
colloc33 = [(0, 2), (1, 2), (2, 2), (3, 2)]
def get_collocations3(clist, qt, cids):
    for t in permutations(qt):
        if t[1] != '*':
            for i in colloc3:
                dt = (i[0] + 1, i[1] + 1)
                if EsAdaptor.collocation3(t, dt, defaultDB, cids, 0)['hits']['total']:
                    clist.append({
                        'type': '%s %s %s %s %s' % (t[0], deps[i[0]], t[1], deps[i[1]], t[2]),
                        'label': 'Colloc%d' % len(clist),
                        'colloc': '%s %s %s %s %s %s' % (t[0], t[1], t[2], dt[0], dt[1], 0),
                    })
        if t[2] != '*':
            for i in colloc33:
                dt = (i[0] + 1, i[1] + 1)
                if EsAdaptor.collocation3(t, dt, defaultDB, cids, 1)['hits']['total']:
                    clist.append({
                        'type': '%s %s %s %s %s' % (t[0], t[1], deps[i[0]], deps[i[1]], t[2]),
                        'label': 'Colloc%d' % len(clist),
                        'colloc': '%s %s %s %s %s %s' % (t[0], t[1], t[2], dt[0], dt[1], 1),
                    })


def collocation_list(mqt, cids):
    clist = []
    if len(mqt) == 1:
        mqt.append('*')
    for i in range(len(mqt) - 1):
        get_collocations(clist, list(mqt), i, cids)
    return clist
    

def collocation3_list(mqt, cids):
    clist = []
    if len(mqt) < 3:
        mqt.append('*')
    if len(mqt) == 3:
        get_collocations3(clist, list(mqt), cids)
    if len(mqt) == 2:
        get_collocations(clist, list(mqt), 0, cids)
    return clist