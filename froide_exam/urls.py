from django.urls import path

from .views import index, private_copy, sent, state_view, upload_exams

urlpatterns = [
    path("", index, name="exam-index"),
    path("gesendet/", sent, name="exam-sent"),
    path("privatkopie/", private_copy, name="exam-private-copy"),
    path("upload/", upload_exams, name="upload-exams"),
    path("<slug:state_slug>/", state_view, name="exam-state"),
]
