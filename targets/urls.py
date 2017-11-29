from django.conf.urls import patterns, include, url

urlpatterns = [
    url(r'^$', 'targets.views.targets'),
    url(r'^(?P<target_pk>.{32})/$', 'targets.views.target'),
    url(r'^(?P<target_pk>.{32})/annotations/$', 'targets.views.annotations'),
    url(r'^(?P<target_pk>.{32})/annotations/(?P<annotation_pk>.+)$', 'targets.views.annotation')
]
