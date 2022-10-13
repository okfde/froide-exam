from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import Subject, State, Curriculum, ExamRequest, PrivateCopy


class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


class StateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "legal_status",
    )
    raw_id_fields = ("publicbody",)


class CurriculumAdmin(admin.ModelAdmin):
    list_display = (
        "state_name",
        "name",
        "start_year",
        "end_year",
    )


class ExamRequestAdmin(admin.ModelAdmin):
    date_hierarchy = "timestamp"
    list_filter = ("foirequest__status", "foirequest__resolution", "curriculum")
    list_display = (
        "name",
        "timestamp",
        "link",
    )
    raw_id_fields = ("foirequest",)

    def name(self, obj):
        return obj.__str__()

    def link(self, obj):
        url = None
        title = _("Externer Link")

        if obj.url:
            url = obj.url
        elif obj.foirequest:
            url = obj.foirequest.url
            title = obj.foirequest.title
        else:
            return None

        return format_html('<a href="{}" target="_blank">{}</a>', url, title)


class PrivateCopyAdmin(admin.ModelAdmin):
    list_display = ("token",)


admin.site.register(Subject, SubjectAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Curriculum, CurriculumAdmin)
admin.site.register(ExamRequest, ExamRequestAdmin)
admin.site.register(PrivateCopy, PrivateCopyAdmin)
