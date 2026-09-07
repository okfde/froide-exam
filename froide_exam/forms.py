from django import forms
from django.forms import ModelForm

from froide.helper.widgets import BootstrapSelect

from .models import ExamRequest
from .tasks import store_exam_upload


class ExamUploadForm(ModelForm):
    class Meta:
        model = ExamRequest
        fields = ["start_year", "subject", "curriculum"]
        widgets = {
            "start_year": forms.NumberInput(attrs={"class": "form-control"}),
            "subject": BootstrapSelect(),
            "curriculum": BootstrapSelect(),
        }

    def save(self, user):
        instance = super().save(commit=True)

        upload_list = self.data.getlist("upload")
        store_exam_upload.delay(instance.id, upload_list, user.id)

        return instance
