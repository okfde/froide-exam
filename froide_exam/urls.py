from django.conf.urls import url

from .views import (
    index, curriculum_view
)

urlpatterns = [
    url(r'^$', index, name='exam-index'),
    url(r'^(?P<curriculum_slug>[\w-]+)/$', curriculum_view,
        name='exam-curriculum'),
]
