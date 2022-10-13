from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import gettext_lazy as _


@apphook_pool.register
class ExamCMSApp(CMSApp):
    name = _("Exam CMS App")
    app_name = "froide_exam"

    def get_urls(self, page=None, language=None, **kwargs):
        return ["froide_exam.urls"]
