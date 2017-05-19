from django.conf.urls import url
import views

urlpatterns = [
    url(r'^comment/$', views.comment_view, name='comment'),
]
