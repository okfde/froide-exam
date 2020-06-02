from django.utils.translation import gettext_lazy as _
from django.db import models

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import Curriculum


@plugin_pool.register_plugin
class ExamCurriculumPlugin(CMSPluginBase):
    module = _("Froide Exam")
    name = _("Exam Curriculum Overview")
    render_template = "froide_exam/plugins/exam_curriculum.html"

    def render(self, context, instance, placeholder):
        context = super().render(context, instance, placeholder)
        curriculums = Curriculum.objects.all().annotate(
            request_count=models.Count(
                'examrequest',
                filter=models.Q(examrequest__foirequest__isnull=False)
            )
        )
        context.update({
            'curriculums': curriculums
        })
        return context
