from collections import defaultdict

from django.utils.translation import gettext_lazy as _
from django.db import models

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import Curriculum, KIND_CHOICES


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

        states = defaultdict(lambda: [])
        for curriculum in curriculums:
            jurisdictions = curriculum.jurisdictions.all()
            s = tuple(sorted(map(lambda juris: juris.slug, jurisdictions)))
            curriculum.kindText = list(filter(lambda kind: kind[0] == curriculum.kind, KIND_CHOICES))[0][1]
            states[s].append(curriculum)

        context.update({
            'curriculums': curriculums,
            'states': states.values()
        })
        return context
