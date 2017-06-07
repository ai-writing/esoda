from django.conf.urls import url, include
import views

urlpatterns = [
    url(r'', include('registration.backends.default.urls')),
    # url(r'', include('django.contrib.auth.urls')),
    
    # urls for profile pages
    url(r'^domain/$', views.domain_view, name='domain'),
    url(r'^personal/$', views.personal_view, name='personal'),
    url(r'^favorites/$', views.favorites_view, name='favorites'),
    url(r'^tree/$', views.tree, name='dept_tree'),
]
