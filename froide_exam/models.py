from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from froide.publicbody.models import PublicBody, Jurisdiction
from froide.foirequest.models import FoiRequest

from .utils import MIN_YEAR, MAX_YEAR


class Subject(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField()

    class Meta:
        verbose_name = ('exam subject')
        verbose_name_plural = _('exam subjects')

    def __str__(self):
        return self.name


class Curriculum(models.Model):
    name = models.CharField(max_length=255)
    jurisdiction = models.ForeignKey(
        Jurisdiction, on_delete=models.CASCADE
    )
    publicbody = models.ForeignKey(
        PublicBody, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    start_year = models.DateField(null=True, blank=True)
    end_year = models.DateField(null=True, blank=True)
    kind = models.CharField(max_length=100, choices=(
        ('abitur', _('Abitur')),
    ))

    subjects = models.ManyToManyField(Subject)

    class Meta:
        verbose_name = ('curriculum')
        verbose_name_plural = _('curricula')

    def __str__(self):
        return self.name

    def get_min_max_year(self):
        min_year = self.start_year.year if self.start_year else MIN_YEAR
        max_year = self.end_year.year if self.end_year else MAX_YEAR
        return min_year, max_year

    def is_valid_year(self, year):
        min_year, max_year = self.get_min_max_year()
        return min_year <= year <= max_year


class ExamRequest(models.Model):
    subject = models.ForeignKey(
        Subject, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    year = models.DateField()
    curriculum = models.ForeignKey(
        Curriculum, null=True, blank=True,
        on_delete=models.SET_NULL
    )

    timestamp = models.DateTimeField(default=timezone.now)
    foirequest = models.ForeignKey(
        FoiRequest, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _('exam request')
        verbose_name_plural = _('exam requests')
        ordering = ('-timestamp',)

    def __str__(self):
        return '{subject} {year} {curriculum}'.format(
            subject=self.subject,
            year=self.year,
            curriculum=self.curriculum
        )
