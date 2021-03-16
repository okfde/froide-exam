from django.conf.urls import url

from .views import (index, state_view, sent, private_copy)

urlpatterns = [
    url(r'^$', index, name='exam-index'),
    url(r'^gesendet/$', sent, name='exam-sent'),
    url(r'^privatkopie/$', private_copy,
        name='exam-private-copy'),
    url(r'^(?P<state_slug>[\w-]+)/$', state_view,
        name='exam-state'),
]
