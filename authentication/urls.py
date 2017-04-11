from django.conf.urls import url, include


urlpatterns = [
    url(r'', include('registration.backends.default.urls')),
    url(r'', include('django.contrib.auth.urls')),
]
