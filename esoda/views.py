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
	return render(request, 'esoda/index.html', info);

def result_view(request):
	return render(request, 'esoda/result.html', {});
