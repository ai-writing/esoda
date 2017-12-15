from django.conf.urls import url
from django.views.generic.base import TemplateView
##???

from . import views

urlpatterns = [
    url(r'^monitor/$', views.monitor_view, name='monitor_view'),
]
