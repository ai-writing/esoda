# -*- coding: utf-8 -*-
from django.shortcuts import render

# Create your views here.
def home_view(request):
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
		'count_of_favorite': 12049
	}
	return render(request, 'esoda/index.html', info)

def result_view(request):
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

	dictionary = {
		'word': 'quality',
        'english': u'[\'kwɒlɪtɪ]',
        'american': u'[\'kwɑləti]',
        'explanationList': [
          u'n. 质量，[统计] 品质；特性；才能',
          u'adj. 优质的；高品质的；<英俚>棒极了'
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

	exampleList = []
	for i in range(1, 51):
		exampleList.append({
    		'label': i,
    		'content': 'The crucial <strong>quality</strong> of this active assimilation was that it guaranteed a certain depth in the individual meteorologist\'s interpretation of the information.',
    		'source': 'UIST\'07. M. Morris et. al.SearchTogether: an interface for collaborative web search.',
    		'heart_number': 129
    	})

	q = 'quality'
	info = {
		'r': r,
		'q': q,
		'dictionary': dictionary,
		'suggestion': suggestion,
		'example_number': 1209,
		'search_time': 0.1,
		'exampleList': exampleList
	}
	return render(request, 'esoda/result.html', info)
