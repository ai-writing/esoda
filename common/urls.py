from django.conf.urls import url
from . import views

app_name = 'common'
urlpatterns = [
    url(r'^comment/$', views.comment_view, name='comment'),
]
