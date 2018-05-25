from django.conf.urls import url
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    url(r'^$', views.esoda_view, name='esoda'),
    url(r'^suggest/$', views.dict_suggest_view, name='dict_suggest'),
    url(r'^sentences/$', views.sentence_view, name='sentences'),
    url(r'^collocation/$', views.syn_usageList_view, name='collocation'),
    url(r'^guide/$', TemplateView.as_view(template_name='esoda/guide.html'), name='guide'),
    url(r'^about_us/$', TemplateView.as_view(template_name='esoda/about_us.html'), name='about_us')
]
