from django.db import models
from django.utils.translation import gettext_lazy as _

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import Curriculum, State


@plugin_pool.register_plugin
class ExamCurriculumPlugin(CMSPluginBase):
    module = _("Froide Exam")
    name = _("Exam Curriculum Overview")
    render_template = "froide_exam/plugins/exam_curriculum.html"

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)

        states = State.objects.all()
        curricula = []

        for state in states:
            curricula = Curriculum.objects.filter(state=state).annotate(
                request_count=models.Count(
                    "examrequest",
                    filter=models.Q(examrequest__foirequest__isnull=False),
                )
            )
            state.curricula = curricula

        states = sorted(
            states,
            key=lambda s: s.needs_request() or s.legal_status == "public",
            reverse=True,
        )

        context.update({"states": states})
        return context
