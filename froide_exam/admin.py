from django.contrib import admin

from .models import Subject, Curriculum, ExamRequest


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('jurisdiction', 'start_year', 'end_year', 'kind')
    raw_id_fields = ('publicbody',)


class ExamRequestAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_filter = ('foirequest__status', 'foirequest__resolution',)
    raw_id_fields = ('foirequest',)


admin.site.register(Subject, SubjectAdmin)
admin.site.register(Curriculum, CurriculumAdmin)
admin.site.register(ExamRequest, ExamRequestAdmin)
