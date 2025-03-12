# -*- encoding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class FroideExamConfig(AppConfig):
    name = "froide_exam"
    verbose_name = _("Froide Exam App")

    def ready(self):
        from froide.foirequest.models import FoiRequest

        from .listeners import connect_request_object, hide_attachments

        FoiRequest.request_created.connect(connect_request_object)
        FoiRequest.message_received.connect(hide_attachments)
