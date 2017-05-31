#!/usr/bin/env python
# encoding: utf-8
from .EsAdaptor import EsAdaptor
from .utils import cleaned_sentence
import views
import time
esi = 'corpus_tree'
esd = 'bnc_tree'
VNJ = ('V', 'N', 'ADJ')  # V&N&ADJ
NADV = ('V', 'N', 'ADJ', 'PRT')  # NON ADV
AITEM = {'V', 'N', 'ADJ', 'PRT', 'ADV', '(modified)', '...'}  # ALL SPECIAL ITEM
RITEM = {'V', 'N', 'ADJ', 'PRT', 'ADV', '...'}  # TO REPLACE


def process_phase1(res, t):  # from source to phrase
    if 'hits' not in res:
        return []

    def filter_thp(key, a):
        return [dw[key] for dw in a]

    def select_thp(its, t):
        return [j for i, j in enumerate(t) if i not in its]

    def join2lists(a, b, j):
        return a[:j] + b + a[j + 1:]

    def modifiedN(ts, hls, ps, e, lenFlag):
        modN = 0
        if e == 'N' and not [p for p in ps if p not in VNJ]:
            modN = int(lenFlag)
            if ts[-1] in t and not lenFlag:  # graphical *user interface --> g i
                its = filter_list(ts, list(t))
                ts, hls, ps = select_thp(its, ts), select_thp(its, hls), select_thp(its, ps)
        return ts, hls, ps, modN

    def modifiedN2(ts, hls, ps, e):
        if e == 'N' and not [p for p in ps if p not in VNJ]:
            its = range(len(ts) - 2)
            ts, hls, ps = select_thp(its, ts), select_thp(its, hls), select_thp(its, ps)
        return ts, hls, ps

    def extend_fa_thp(ts, hls, ps, e):
        if modes['p']:
            fi, fj = modes['p'].split('_')
            fi, fj = int(fi), int(fj)
            fi, e = src['d'][fi]['w'], src['d'][fi]['e']
            pts, phls, pps = filter_thp('t', fi), filter_thp('i', fi), filter_thp('p', fi)
            ts, hls, ps = join2lists(pts, ts, fj), join2lists(phls, hls, fj), join2lists(pps, ps, fj)
        return ts, hls, ps, e

    def extend_child_thp(ts, hls, ps, i, modes):
        pts, phls, pps = filter_thp('t', modes['w']), filter_thp('i', modes['w']), filter_thp('p', modes['w'])
        pts, phls, pps = modifiedN2(pts, phls, pps, modes['e'])
        ts, hls, ps = join2lists(ts, pts, i), join2lists(hls, phls, i), join2lists(ps, pps, i)
        return ts, hls, ps

    def filter_list(ts, nt):
        its = []
        for i in range(len(ts)):
            if ts[i] in nt:
                nt.remove(ts[i])
            else:
                its.append(i)
        return its

    def compond(ts, hls, ps, e, sp):
        return [' '.join(ts), ' '.join(hls), ' '.join(ps), e, sp]

    res1 = []
    for ht in res['hits']:
        src = ht['_source']
        col = []
        child = dict([(modes['p'], i) for i, modes in enumerate(src['d'])])
        ni = -1
        for modes in src['d']:
            ni += 1
            ts, hls, ps = filter_thp('t', modes['w']), filter_thp('i', modes['w']), filter_thp('p', modes['w'])
            e, flag = modes['e'], int(bool([i for i in t if i not in ts]))
            ts, hls, ps, modN = modifiedN(ts, hls, ps, e, len(t) == 1)
            if flag == 0:
                col.append(compond(ts, hls, ps, e, ''))
                nt, lens = list(t), len(ts)
                if modN != 1 and not [i for i in range(lens) if ts[i] not in nt and ps[i] in NADV]:
                    flag = 2

            if flag:
                # flag = 0 --> not in a phrase
                if flag == 1 and [i for i in t if i in ts]:
                    if modes['p']:
                        nts = filter_thp('t', src['d'][int(modes['p'].split('_')[0])]['w'])
                        if not [i for i in t if i not in nts]:
                            continue
                        ts, hls, ps, e = extend_fa_thp(ts, hls, ps, e)
                        if not [i for i in t if i not in ts]:
                            col.append(compond(ts, hls, ps, e, ''))
                    # in a pharse extended with a parent pharase
                if flag == 2:
                    # continue
                    if modes['p']:
                        nts, nhls, nps, ne = extend_fa_thp(ts, hls, ps, e)
                        col.append(compond(nts, nhls, nps, ne, ''))
                    for i in range(len(ts)):
                        pt = "%s_%s" % (ni, i)
                        if ts[i] in t and pt in child:
                            nts, nhls, nps = extend_child_thp(ts, hls, ps, i, src['d'][child[pt]])
                            col.append(compond(nts, nhls, nps, e, ''))

        if col:
            res1.append({
                'id': ht['_id'],
                't': src['t'],
                'c': col
            })

    return res1


def process_phase2(res1, t, md, num, mps):
    def process_phase2_inner(ts, hs, ps, e, sp, nt):
        def append_res():
            if not nt:
                swords = ' '.join(words)
                if not md and swords not in mps:
                    mps[swords] = []
                if md and swords == md:
                    if len(mps[swords]) >= num:
                        mps[swords].append(0)
                    else:
                        mps[swords].append({'t': tokens, 'i': hls, 's': ht['t'], 'id': ht['id']})
                if not md:
                    mps[swords].append(0)

        def appending():
            hls.append(hs[i])
            if ts[i] in nt:
                nt.remove(ts[i])
                words.append(ts[i])
                tokens.append(ts[i])
                return True
            return False

        tokens, words, hls, lens = [], [], [], len(ts)
        if e == 'N':
            if not [p for p in ps if p not in ('V', 'N', 'ADJ')]:
                if ts[-1] in nt:
                    flag = (len(nt) == 1)
                    if flag:
                        words.append('...')
                    examples = []
                    for i in range(lens):
                        if ts[i] in nt or flag:
                            if not appending():
                                examples.append(ts[i])
                    tokens.insert(-1, examples)
                    if flag:
                        tokens.insert(-1, '(modified)')
                else:
                    for i in range(lens):
                        if ts[i] in nt or i == lens - 1:
                            if not appending():
                                words.append(ps[i])
                                tokens.append(ts[i])
                    tokens.insert(-1, '')
                words.insert(-1, '(modified)')
                append_res()
                return
        # (modified) N
        checkADV = bool([i for i in range(lens) if ts[i] not in nt and ps[i] in NADV]) or 'no_ADV' in sp
        for i in range(lens):
            if checkADV and ps[i] == 'ADV':
                continue
            if not appending():
                words.append(ps[i])
                tokens.append(ts[i])
        append_res()
        # other

    for ht in res1:
        for col in ht['c']:
            ts, hs, ps, e, sp = col[0].split(' '), col[1].split(' '), col[2].split(' '), col[3], col[4]
            process_phase2_inner(ts, hs, ps, e, sp, list(t))

    return mps


def process_query(t, md, num):
    mps = {}
    if md:
        mps[md] = []
    res = EsAdaptor.search_tree(t, esi, esd, 0, 10000)
    res1 = process_phase1(res, t)
    res2 = process_phase2(res1, t, md, num, mps)
    return res2


def process_usage_list(t):
    t = [x for x in t if x not in AITEM]
    res = process_query(t, '', 0)
    t = sorted(res.items(), key=lambda x: -len(x[1]))[:10]
    return [{"type": x[0], "label": "usage%d" % i} for i, x in enumerate(t)]


def process_usage_usage_list(t, md):
    t = [x for x in t if x not in AITEM]
    res = process_query(t, md, 2**20)
    ws = [{'content': md, 'count': len(res[md])}]

    mmd = md.split(' ')
    mps = {}
    for wt in res[md]:
        for i in range(len(mmd)):
            if mmd[i] in RITEM:
                org = mmd[i]
                if isinstance(wt['t'][i], list):
                    for j in wt['t'][i]:
                        mmd[i] = j
                        key = ' '.join(mmd)
                        mps[key] = mps.get(key, 0) + 1
                else:
                    mmd[i] = wt['t'][i]
                    key = ' '.join(mmd)
                    mps[key] = mps.get(key, 0) + 1
                mmd[i] = org
    rs = sorted(mps.items(), key=lambda x: -x[1])
    for i, j in enumerate(rs):
        if i < 10 or j[1] > 20:
            ws.append({'content': j[0], 'count': j[1]})
    return ws


def process_sentence_list(t, md):
    t = [x for x in t if x not in AITEM]
    time1 = time.time()
    res = process_query(t, md, views.displayNum)
    time2 = time.time()
    sr = {'time': round(time2 - time1, 2), 'total': len(res[md]), 'sentence': None}
    sr['sentence'] = [{
        'content': cleaned_sentence(x['s'], x['i']),
        'heart_number': 129,
        'source': ''}
        for x in res[md][:views.displayNum]]
    return sr
