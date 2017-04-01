from django.conf.urls import url
from django.views.generic.base import TemplateView


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='esoda/index.html'), name='index'),
    url(r'^result/$', TemplateView.as_view(template_name='esoda/result.html'), name='result'),
]
