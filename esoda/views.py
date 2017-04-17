# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse

import xml.sax
import json
import requests


# Create your views here.
def esoda_view(request):
    q = request.GET.get('q', '').strip()

    # No query - render index.html
    if not q:
        info = {
            'feedbackList': [
                {
                    'content': u'无产阶级政党的党章是以马克思主义党的学说为指导，结合党的建设的实践而制定的党的生活准则和行为规范。',
                    'user_name': u'潘星宇'
                },
                {
                    'content': u'无产阶级政党的党章是以马克思主义党的学说为指导，结合党的建设的实践而制定的党的生活准则和行为规范。',
                    'user_name': u'潘星宇'
                }
            ],
            'count_of_favorite': 12049,
            'tab': 'index'
        }
        return render(request, 'esoda/index.html', info)

    # With query - render result.html
    usageList = []
    for i in range(1, 28):
        usageList.append({
            'content': 'improve...quality',
            'count': 609
        })
    r = {
        'domain': u'人机交互',
        'count': 222,
        'synonymous': [
          'trait',
          'characteristic',
          'feature',
          'attribute',
          'property',
          'ability',
          'talent',
          'capability'
        ],
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
            {
                'type': u'quality (主谓)*',
                'label': 'Colloc1',
                'usageList': usageList,
            },
            {
                'type': u'quality (修饰)*',
                'label': 'Colloc2',
                'usageList': usageList,
            },
            {
                'type': u'quality (介词)*',
                'label': 'Colloc3',
                'usageList': usageList
            },
            {
                'type': u'*(修饰) quality',
                'label': 'Colloc4',
                'usageList': usageList
            }
        ]
    }

    suggestion = {
        'relatedList': [
            'high quality',
            'improve quality',
            'ensure quality',
            '*(修饰) quality'
        ],
        'hotList': [
            'interaction',
            'algorithm',
            'application'
        ]
    }

    info = {
        'r': r,
        'q': q,
        'suggestion': suggestion,
    }

    YOUDAO_SEARCH_URL = 'http://dict.youdao.com/jsonapi?dicts={count:1,dicts:[[\"ec\"]]}&q=%s'
    jsonString = requests.get(YOUDAO_SEARCH_URL % q, timeout=10).text
    jsonObj = json.loads(jsonString.encode('utf-8'))

    if jsonObj.has_key('simple') and jsonObj.has_key('ec'):
        dictionary = {
            'word': q,
            'english': jsonObj['simple']['word'][0].get('ukphone',''),
            'american': jsonObj['simple']['word'][0].get('usphone',''),
            'explanationList': []
        }
        for explain in jsonObj['ec']['word'][0]['trs']:
            dictionary['explanationList'].append(explain['tr'][0]['l']['i'][0])
        info['dictionary'] = dictionary

    return render(request, 'esoda/result.html', info)

def sentence_view(request):
    # Empty q - load the initial exampleList
    if not request.GET:
        exampleList = []
        for i in range(1, 51):
            exampleList.append({
                'content': 'The crucial <strong>quality</strong> of this active assimilation was that it guaranteed a certain depth in the individual meteorologist\'s interpretation of the information.',
                'source': 'UIST\'07. M. Morris et. al.SearchTogether: an interface for collaborative web search.',
                'heart_number': 129,
            })

        info = {
            'example_number': 1209,
            'search_time': 0.1,
            'exampleList': exampleList
        }
    # With collocation category q - load the specific exampleList
    else:
        q = request.GET.keys()[0]
        exampleList = []
        for i in range(1, 34):
            exampleList.append({
                'content': 'The crucial <strong>quality</strong> of this active assimilation was that it guaranteed a certain depth in the individual meteorologist\'s interpretation of the information.',
                'source': 'UIST\'07. M. Morris et. al.SearchTogether: an interface for collaborative web search.',
                'heart_number': 222,
            })

        info = {
            'example_number': 33,
            'search_time': 0.5,
            'exampleList': exampleList
        }
    return render(request, 'esoda/sentence_result.html', info)

class DictHandler( xml.sax.ContentHandler ):
    def __init__(self):
        self.suggest = []
        self.CurNum = 0
        self.CurTag = ''
        self.category = ''

    def startElement(self, tag, attributes):
        self.CurTag = tag
        if tag == 'item':
            self.suggest.append({})

    def endElement(self, tag):
        if tag == 'item':
            self.suggest[self.CurNum]['category'] = self.category
            self.category = ''
            self.CurNum += 1
        self.CurTag = ''

    def characters(self, content):
        if self.CurTag == 'title':
            self.suggest[self.CurNum]['label'] = content
            if content.find(' ') < 0:
                self.category = 'Words'
            else:
                self.category = 'Expressions'
        elif self.CurTag == 'explain':
            self.suggest[self.CurNum]['desc'] = content

YOUDAO_SUGGEST_URL = 'http://dict.youdao.com/suggest?ver=2.0&le=en&num=10&q=%s'
def dict_suggest_view(request):
    q = request.GET.get('term', '')
    r = {}
    try:
        xmlstring = requests.get(YOUDAO_SUGGEST_URL % q, timeout=10).text
        parser = xml.sax.make_parser()
        parser.setFeature(xml.sax.handler.feature_namespaces, 0)

        Handler = DictHandler()
        xml.sax.parseString(xmlstring.encode('utf-8'), Handler)
        r['suggest'] = Handler.suggest
    except Exception as e:
        print repr(e)
    return JsonResponse(r)

def guide_view(request):
    info = {
        'tab': 'guide'
    }
    return render(request, 'esoda/guide.html', info)

# Views for profile urls
def domain_view(request):
    info = {
        'tab': 'profile',
        'profileTab': 'domain'
    }
    return render(request, 'esoda/profile/domain_select.html', info)
def personal_view(request):
    info = {
        'tab': 'profile',
        'profileTab': 'personal'
    }
    return render(request, 'esoda/profile/personal.html', info)
def favorites_view(request):
    exampleList = []
    for i in range(1, 51):
        exampleList.append({
            'content': 'The crucial <strong>quality</strong> of this active assimilation was that it guaranteed a certain depth in the individual meteorologist\'s interpretation of the information.',
            'source': 'UIST\'07. M. Morris et. al.SearchTogether: an interface for collaborative web search.',
            'heart_number': 129,
        })

    info = {
        'example_number': 50,
        'search_time': 0.1,
        'exampleList': exampleList,
        'tab': 'profile',
        'profileTab': 'favorites'
    }
    return render(request, 'esoda/profile/favorites.html', info)

