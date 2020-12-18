from django.conf.urls import url

from .views import (index, state_view)

urlpatterns = [
    url(r'^$', index, name='exam-index'),
    url(r'^(?P<state_slug>[\w-]+)/$', state_view,
        name='exam-state'),
]
