# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from common.mongodb import MONGODB
from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def monitor_view(request):
    user = request.user
    db = MONGODB.esl
    db_sentences = MONGODB.sentences
    db_dblp = MONGODB.dblp
    update = db_dblp.log.find({'type': 'update'})
    update_time = update[0]['time']
    ccfa = []
    aN = an = ap = 0
    for v in db.venues.find({'ccf': 'A'}):
        N = db.papers.find({'venue': v['_id'], 'info.type': {'$ne': 'proceedings'}}).count()
        n = db.papers.find({'venue': v['_id'], 'downloaded': True}).count()
        aN += N
        an += n
        S = v.get('shortName', v['fullName'])
        s = v['dblp']
        name = '%s (%s)' % (S, s) if user.is_superuser else S
        senNum = db_sentences[s].count()
        field = v['field']
        impFac = v['impactFactor']
        ccfa.append({'name': name, 'n': n, 'N': N, 'p': float(n * 100) / N, 'senNum': senNum, 'field': field,
                     'impactFactor': impFac})
    ccfb = []
    bN = bn = bp = 0
    for v in db.venues.find({'ccf': 'B', 'c': {'$exists': True}}):
        N = db.papers.find({'venue': v['_id'], 'info.type': {'$ne': 'proceedings'}}).count()
        n = db.papers.find({'venue': v['_id'], 'downloaded': True}).count()
        bN += N
        bn += n
        S = v.get('shortName', v['fullName'])
        s = v['dblp']
        name = '%s (%s)' % (S, s) if user.is_superuser else S
        senNum = db_sentences[s].count()
        field = v['field']
        impFac = v['impactFactor']
        ccfb.append({'name': name, 'n': n, 'N': N, 'p': float(n * 100) / N, 'senNum': senNum, 'field': field,
                     'impactFactor': impFac})

    ccfa.sort(key = lambda v: v['name'])
    ccfb.sort(key = lambda v: v['name'])
    ap = float(an * 100) / aN
    bp = float(bn * 100) / bN
    return render(request, 'monitor/monitor.html',
                  {'update_time': update_time, 'ccfa': ccfa, 'ccfb': ccfb, 'aN': aN, 'an': an, 'bN': bN, 'bn': bn,
                   'ap': ap, 'bp': bp})
