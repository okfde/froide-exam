from django.conf.urls import url

from .views import (index, state_view, sent)

urlpatterns = [
    url(r'^$', index, name='exam-index'),
    url(r'^gesendet/$', sent, name='exam-sent'),
    url(r'^(?P<state_slug>[\w-]+)/$', state_view,
        name='exam-state'),
]
