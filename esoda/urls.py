from django.conf.urls import url
from django.views.generic.base import TemplateView
import views


urlpatterns = [
    #url(r'^$', TemplateView.as_view(template_name='esoda/index.html'), name='index'),
    #url(r'^result/$', TemplateView.as_view(template_name='esoda/result.html'), name='result'),
    url(r'^$', views.home_view, name='index'),
    url(r'^result/$', views.result_view, name='result'),
]
