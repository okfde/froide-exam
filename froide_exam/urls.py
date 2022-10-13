from django.urls import path

from froide.api import api_router

from .api_views import StateViewSet, CurriculumViewSet, SubjectViewSet
from .views import index, state_view, sent, private_copy

urlpatterns = [
    path("", index, name="exam-index"),
    path("gesendet/", sent, name="exam-sent"),
    path("privatkopie/", private_copy, name="exam-private-copy"),
    path("<slug:state_slug>/", state_view, name="exam-state"),
]

api_router.register(r"examsubject", SubjectViewSet, basename="examsubject")
api_router.register(r"examstate", StateViewSet, basename="examstate")
api_router.register(r"examcurriculum", CurriculumViewSet, basename="examcurriculum")
