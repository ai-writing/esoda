"""esodawebsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.views.generic.base import TemplateView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
]

urlpatterns += [
    url(r'^$', TemplateView.as_view(template_name='esoda/index.html'), name='index'),
    url(r'^result/$', TemplateView.as_view(template_name='esoda/result.html'), name='result'),
    url(r'^404/$', TemplateView.as_view(template_name='404.html'), name='404'),
    url(r'^500/$', TemplateView.as_view(template_name='500.html'), name='500'),
]
