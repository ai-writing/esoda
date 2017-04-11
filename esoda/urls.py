from django.conf.urls import url
from django.views.generic.base import TemplateView

from . import views


urlpatterns = [
    url(r'^$', views.esoda_view, name='esoda'),
    url(r'^result/$', views.result_view, name='result'),
    url(r'^suggest/$', views.dict_suggest_view, name='dict_suggest'),
    url(r'^sentences/$', views.sentence_view, name='sentences'),
]
