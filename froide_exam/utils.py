from urllib.parse import urlencode

from django.utils import timezone
from django.urls import reverse


TODAY = timezone.now().date()
MIN_YEAR = 2010
# max year is this year starting in July, otherwise year before
MAX_YEAR = TODAY.year if TODAY.month >= 7 else TODAY.year - 1
YEARS = list(range(MIN_YEAR, MAX_YEAR + 1))

REFERENCE_NAMESPACE = 'examvsp:'


class SubjectYear(object):

    def __init__(self, user=None, subject=None, year=None, same_requests=None):
        self.subject = subject
        self.year = year
        self.user = user
        self.same_requests = same_requests

    def __str__(self):
        return '{}: {}'.format(self.subject, self.year)

    def get_reference(self, curriculum):
        return '{namespace}{curriculum_id}:{subject_id}:{year}'.format(
            namespace=REFERENCE_NAMESPACE,
            curriculum_id=curriculum.id,
            subject_id=self.subject.id,
            year=self.year
        )

    @property
    def exam_request(self):
        if self.exam_requests:
            # if there's just one, take that one
            er = self.exam_requests[0]

            # if there are multiple ones to choose from,
            # prefer one with a url
            # or a successful one
            if len(self.exam_requests) > 1:
                for request in self.exam_requests:
                    if request.foirequest and request.foirequest.resolution == 'successful':
                        er = request
                        break

                for request in self.exam_requests:
                    if request.url:
                        er = request
                        break
            
            return er
        return None

    @property
    def exam_foirequest(self):
        if not self.exam_requests:
            return None
        er = self.exam_requests[0]
        if (not er.foirequest or
                er.foirequest.status == 'awaiting_user_confirmation'):
            return None
        return er

    @property
    def request_awaiting_user(self):
        if not self.exam_request:
            return False
        if not self.exam_request.foirequest:
            return False
        er = self.exam_request
        return er.foirequest.status == 'awaiting_user_confirmation'

    @property
    def request_pending(self):
        if not self.exam_request:
            return False
        if not self.exam_request.foirequest:
            return
        fr = self.get_same_request() or self.exam_request.foirequest
        return not fr.status_is_final()

    @property
    def request_failed(self):
        if not self.exam_request:
            return False
        if not self.exam_request.foirequest:
            return
        fr = self.get_same_request() or self.exam_request.foirequest
        return 'successful' not in fr.resolution

    def can_request(self):
        if not self.curricula:
            return
        curriculum = self.curricula[0]
        if not self.state and not self.state.needs_request():
            return False
        if self.exam_request and self.exam_request.url:
            return False
        if not self.exam_foirequest:
            return True
        if self.state and self.state.legal_status == 'request':
            return False
        if not self.user.is_authenticated:
            return True
        if self.has_requested():
            return False
        return True

    def has_requested(self):
        return self.get_same_request() is not None

    def get_same_request(self):
        if not self.exam_request:
            return
        if self.exam_request.foirequest_id in self.same_requests:
            return self.same_requests[self.exam_request.foirequest_id]

    def is_one_click(self):
        if not self.curricula:
            return
        curriculum = self.curricula[0]
        if not self.state.legal_status == 'request_not_publish':
            return
        if not self.exam_requests:
            return
        return self.exam_requests[0].foirequest

    def make_request_url(self):
        if not self.curricula:
            return
        if hasattr(self, '_request_url'):
            return self._request_url
        curriculum = self.curricula[0]

        pb_slug = self.state.publicbody.slug
        url = reverse('foirequest-make_request', kwargs={
            'publicbody_slug': pb_slug
        })
        kind = curriculum.get_kind_display()
        subject = ('{kind}-Aufgaben im Fach {subject} '
                   'im Jahr {year} in {name}'.format(
                    kind=kind,
                    subject=self.subject,
                    year=self.year,
                    name=curriculum.state.name,
                    ))
        if len(subject) > 250:
            subject = subject[:250] + '...'
        body = (
            'Die Aufgaben, Erwartungshorizonte und Lösungen für die '
            '{kind}-Prüfung im Fach {subject} aus dem Jahr {year} in {name}.'
        ).format(
                subject=self.subject,
                year=self.year,
                kind=kind,
                name=curriculum.state.name
        )
        ref = self.get_reference(curriculum)
        query = {
            'subject': subject.encode('utf-8'),
            'body': body.encode('utf-8'),
            'ref': ref.encode('utf-8'),
            'redirect': '/kampagnen/verschlusssache-pruefung/gesendet'.encode('utf-8'),
        }
        hide_features = (
            'hide_public', 'hide_full_text', 'hide_similar', 'hide_publicbody',
            'hide_draft', 'hide_editing'
        )
        query.update({f: b'1' for f in hide_features})
        query = urlencode(query)
        self._request_url = '%s?%s' % (url, query)
        return self._request_url
