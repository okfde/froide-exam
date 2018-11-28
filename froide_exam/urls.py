from django.conf.urls import url

from .views import (
    index, jurisdiction_view
)

urlpatterns = [
    url(r'^$', index, name='exam-index'),
    url(r'^(?P<jurisdiction_slug>[\w-]+)/$', jurisdiction_view,
        name='exam-jurisdiction'),
]
