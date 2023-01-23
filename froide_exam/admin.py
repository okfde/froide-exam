from datetime import date

from django.contrib import admin, messages
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from froide.foirequest.models import FoiRequest

from .models import Curriculum, ExamRequest, PrivateCopy, State, Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "legal_status",
    )
    raw_id_fields = ("publicbody",)


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = (
        "state_name",
        "name",
        "start_year",
        "end_year",
    )


@admin.register(ExamRequest)
class ExamRequestAdmin(admin.ModelAdmin):
    date_hierarchy = "timestamp"
    list_filter = (
        "curriculum__state",
        "foirequest__status",
        "foirequest__resolution",
        "curriculum",
    )
    list_display = (
        "name",
        "timestamp",
        "link",
    )
    raw_id_fields = ("foirequest",)
    actions = ("set_end_year_to_current", "allow_publication", "disallow_publication")

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

    @admin.action(description=_("Set end year to current year"))
    def set_end_year_to_current(self, request, queryset):
        end_year = date.today().replace(month=12, day=31)
        queryset.update(end_year=end_year)

    def set_not_publishable(self, request, queryset, not_publishable):
        updated = FoiRequest.objects.filter(examrequest__in=queryset).update(
            not_publishable=not_publishable
        )

        self.message_user(
            request,
            ngettext(
                "%d foi request was updated.",
                "%d foi requests were updated.",
                updated,
            )
            % updated,
            messages.SUCCESS,
        )

    @admin.action(description=_("Disallow publication of requests"))
    def disallow_publication(self, request, queryset):
        self.set_not_publishable(request, queryset, True)

    @admin.action(description=_("Allow publication of requests"))
    def allow_publication(self, request, queryset):
        self.set_not_publishable(request, queryset, False)


@admin.register(PrivateCopy)
class PrivateCopyAdmin(admin.ModelAdmin):
    list_display = ("token",)
