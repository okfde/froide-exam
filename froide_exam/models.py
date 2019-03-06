from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.urls import reverse

from cms.models.fields import PlaceholderField

from froide.publicbody.models import PublicBody, Jurisdiction
from froide.foirequest.models import FoiRequest

from .utils import MIN_YEAR, MAX_YEAR


LEGAL_STATUS_CHOICES = (
    ('request', _('Anfragbar')),
    ('request_not_publish', _('Anfragbar (nicht veröffentlichbar)')),
    ('public', _('Schon öffentlich')),
    ('unrequestable', _('Nicht anfragbar')),
)


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
    slug = models.SlugField(default=None, null=True)

    description = models.TextField(blank=True)

    jurisdictions = models.ManyToManyField(
        Jurisdiction,
        related_name='curriculums'
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
    legal_status = models.CharField(
        max_length=100,
        choices=LEGAL_STATUS_CHOICES,
        default='request'
    )

    content_placeholder = PlaceholderField('content')

    subjects = models.ManyToManyField(Subject)

    class Meta:
        verbose_name = ('curriculum')
        verbose_name_plural = _('curricula')
        ordering = ('name',)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        if self.slug:
            return reverse('exam-curriculum', kwargs={
                'curriculum_slug': self.slug
            })
        return ''

    def get_min_max_year(self):
        min_year = self.start_year.year if self.start_year else MIN_YEAR
        max_year = self.end_year.year if self.end_year else MAX_YEAR
        return min_year, max_year

    def is_valid_year(self, year):
        min_year, max_year = self.get_min_max_year()
        return min_year <= year <= max_year

    def needs_request(self):
        return self.legal_status.startswith('request')

    def is_deadend(self):
        return self.legal_status == 'unrequestable'

    def is_oneclick(self):
        return self.legal_status == 'request_not_publish'


class ExamRequest(models.Model):
    subject = models.ForeignKey(
        Subject, null=True, blank=True,
        on_delete=models.SET_NULL
    )
    start_year = models.DateField()
    end_year = models.DateField(null=True, blank=True)
    curriculum = models.ForeignKey(
        Curriculum, null=True, blank=True,
        on_delete=models.SET_NULL
    )

    url = models.URLField(blank=True)
    timestamp = models.DateTimeField(
        blank=True, null=True,
        default=timezone.now
    )
    foirequest = models.ForeignKey(
        FoiRequest,
        null=True, blank=True,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _('exam request')
        verbose_name_plural = _('exam requests')
        ordering = ('-timestamp',)

    def __str__(self):
        return '{subject} {year} {curriculum}'.format(
            subject=self.subject,
            year=self.get_years(),
            curriculum=self.curriculum
        )

    def get_years(self):
        if self.end_year is not None:
            return list(range(self.start_year.year, self.end_year.year + 1))
        return [self.start_year.year]
