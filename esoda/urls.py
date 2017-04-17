from django.conf.urls import url
from django.views.generic.base import TemplateView

from . import views


urlpatterns = [
    url(r'^$', views.esoda_view, name='esoda'),
    url(r'^suggest/$', views.dict_suggest_view, name='dict_suggest'),
    url(r'^sentences/$', views.sentence_view, name='sentences'),
    url(r'^guide/$', views.guide_view, name='guide'),
    # urls for profile pages
    url(r'^domain/$', views.domain_view, name='domain'),
    url(r'^personal/$', views.personal_view, name='personal'),
    url(r'^security/$', views.security_view, name='security'),
    url(r'^favorites/$', views.favorites_view, name='favorites'),
]
