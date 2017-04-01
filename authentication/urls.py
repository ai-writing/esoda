from django.conf.urls import url, include


urlpatterns = [
    url(r'', include('registration.backends.default.urls')),
    # TODO: login
]
