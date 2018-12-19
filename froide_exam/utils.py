from urllib.parse import urlencode

from django.utils import timezone
from django.urls import reverse


TODAY = timezone.now().date()
MIN_YEAR = 2010
# max year is this year starting in July, otherwise year before
MAX_YEAR = TODAY.year if TODAY.month >= 7 else TODAY.year - 1
YEARS = list(range(MIN_YEAR, MAX_YEAR + 1))

REFERENCE_NAMESPACE = 'exam:'


class SubjectYear(object):

    def __init__(self, subject=None, year=None):
        self.subject = subject
        self.year = year

    def __str__(self):
        return '{}: {}'.format(self.subject, self.year)

    def get_reference(self, curriculum):
        return '{namespace}{curriculum_id}:{subject_id}:{year}'.format(
            namespace=REFERENCE_NAMESPACE,
            curriculum_id=curriculum.id,
            subject_id=self.subject.id,
            year=self.year
        )

    def make_request_url(self):
        if not self.curricula:
            return
        if hasattr(self, '_request_url'):
            return self._request_url
        curriculum = self.curricula[0]

        pb_slug = curriculum.publicbody.slug
        url = reverse('foirequest-make_request', kwargs={
            'publicbody_slug': pb_slug
        })
        kind = curriculum.get_kind_display()
        subject = ('{kind}-Aufgaben im Fach {subject} '
                   'aus dem Jahr {year}'.format(
                    kind=kind,
                    subject=self.subject,
                    year=self.year,
                    ))
        if len(subject) > 250:
            subject = subject[:250] + '...'
        body = (
            'Die Aufgaben im Fach {subject} aus dem Jahr {year} '
            'für die {kind}-Prüfung'
        ).format(subject=self.subject, year=self.year, kind=kind)
        ref = self.get_reference(curriculum)
        query = {
            'subject': subject.encode('utf-8'),
            'body': body.encode('utf-8'),
            'ref': ref.encode('utf-8')
        }
        hide_features = (
            'hide_public', 'hide_full_text', 'hide_similar', 'hide_publicbody',
            'hide_draft', 'hide_editing'
        )
        query.update({f: b'1' for f in hide_features})
        query = urlencode(query)
        self._request_url = '%s?%s' % (url, query)
        return self._request_url
