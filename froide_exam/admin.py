from django.contrib import admin

from .models import Subject, State, Curriculum, ExamRequest


class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'legal_status',)
    raw_id_fields = ('publicbody',)

class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('state_name', 'name', 'start_year', 'end_year',)

class ExamRequestAdmin(admin.ModelAdmin):
    date_hierarchy = 'timestamp'
    list_filter = (
        'foirequest__status', 'foirequest__resolution',
        'curriculum')
    raw_id_fields = ('foirequest',)


admin.site.register(Subject, SubjectAdmin)
admin.site.register(State, StateAdmin)
admin.site.register(Curriculum, CurriculumAdmin)
admin.site.register(ExamRequest, ExamRequestAdmin)