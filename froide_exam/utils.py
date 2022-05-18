from urllib.parse import urlencode

from django.utils import timezone
from django.urls import reverse


TODAY = timezone.now().date()
# max year is this year starting in July, otherwise year before
MAX_YEAR = TODAY.year if TODAY.month >= 7 else TODAY.year - 1
MIN_YEAR = MAX_YEAR - 6
YEARS = list(range(MIN_YEAR, MAX_YEAR + 1))

REFERENCE_NAMESPACE = "examvsp:"

# waiting requests with no response in 3 months are stale
# and should be requested by another user again
STALE_THRESHOLD = 90


class SubjectYear(object):
    def __init__(
        self, user=None, subject=None, year=None, same_requests=None, state=None
    ):
        self.subject = subject
        self.year = year
        self.user = user
        self.same_requests = same_requests
        self.state = state

    def __str__(self):
        return "{}: {}".format(self.subject, self.year)

    def get_reference(self, curriculum):
        return "{namespace}{curriculum_id}:{subject_id}:{year}".format(
            namespace=REFERENCE_NAMESPACE,
            curriculum_id=curriculum.id,
            subject_id=self.subject.id,
            year=self.year,
        )

    @property
    def exam_request(self):
        if self.exam_requests:
            er = None

            with_success = None
            with_url = None
            by_user = None

            for request in self.exam_requests:
                if request.foirequest:
                    foirequest = request.foirequest
                    if is_request_stale(foirequest):
                        # this one is stale.
                        # allow to re-request by someone else.
                        if self.user.id != foirequest.user_id:
                            continue

                    if self.user.id == foirequest.user_id:
                        by_user = request

                    if foirequest.resolution == "successful":
                        with_success = request

                if request.url:
                    with_url = request
                    break  # we already have our favorite, so stop

                er = request

            # prefer one with a url, then a successful one,
            # then one created by the current user
            return with_url or with_success or by_user or er
        return None

    @property
    def exam_foirequest(self):
        if not self.exam_requests:
            return None

        def request_valid(er):
            return er.foirequest and er.foirequest.is_sent()

        exam_requests = list(filter(request_valid, self.exam_requests))

        if len(exam_requests) == 0:
            return None

        return exam_requests[-1]

    @property
    def request_awaiting_user(self):
        if not self.exam_request:
            return False
        if not self.exam_request.foirequest:
            return False
        er = self.exam_request
        return er.foirequest.awaits_user_confirmation()

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
        return "successful" not in fr.resolution

    def can_request(self):
        if not self.state and not self.state.needs_request():
            return False
        if self.exam_request and self.exam_request.url:
            return False
        if not self.exam_foirequest:
            return True
        if (
            self.state.legal_status == "request_not_publish"
            and not self.user_requested()
        ):
            return True
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

    def user_requested(self):
        return (
            self.exam_request
            and self.exam_request.foirequest
            and self.user == self.exam_request.foirequest.user
        )

    def is_one_click(self):
        if self.state.legal_status != "request_not_publish":
            return False
        return self.exam_foirequest

    def make_request_url(self):
        if not self.curricula:
            return
        if hasattr(self, "_request_url"):
            return self._request_url
        curriculum = self.curricula[0]

        pb_slug = self.state.publicbody.slug
        url = reverse("foirequest-make_request", kwargs={"publicbody_slug": pb_slug})
        name = curriculum.name
        subject = (
            "{name}-Aufgaben im Fach {subject} "
            "im Jahr {year} in {state}".format(
                name=name,
                subject=self.subject,
                year=self.year,
                state=curriculum.state.name,
            )
        )
        if len(subject) > 250:
            subject = subject[:250] + "..."
        body = (
            "Die Aufgaben, Erwartungshorizonte und Lösungen für die "
            "{name}-Prüfung im Fach {subject} aus dem Jahr {year} in {state}."
        ).format(
            subject=self.subject, year=self.year, name=name, state=curriculum.state.name
        )
        ref = self.get_reference(curriculum)
        redirect_path = "/kampagnen/verschlusssache-pruefung/app/gesendet"
        query = {
            "subject": subject.encode("utf-8"),
            "body": body.encode("utf-8"),
            "ref": ref.encode("utf-8"),
            "redirect": redirect_path.encode("utf-8"),
        }
        hide_features = (
            "hide_public",
            "hide_full_text",
            "hide_similar",
            "hide_publicbody",
            "hide_draft",
            "hide_editing",
        )
        query.update({f: b"1" for f in hide_features})
        query = urlencode(query)
        self._request_url = "%s?%s" % (url, query)
        return self._request_url

    def get_request_state(self):
        if self.request_pending:
            return ("pending", "Schon angefragt")
        elif self.request_failed:
            return ("refused", "Fehlgeschlagen")
        elif self.request_successful:
            return ("successful", "Abgeschlossen")
        else:
            return ("request", "Jetzt anfragen!")

    def display(self):
        if self.exam_request:
            if self.exam_request.url:
                return {
                    "link": self.exam_request.url,
                    "title": "Schon öffentlich",
                    "state": "successful",
                    "icon": "download",
                }
            elif not self.state.is_one_click:
                state, title = self.get_request_state()
                url = self.exam_request.foirequest.get_absolute_url()
                return {"link": url + "#last", "state": state, "title": title}
            elif not self.can_request:
                state, title = self.get_request_state()
                return {
                    "link": self.get_same_request.get_absolute_url(),
                    "state": state,
                    "title": title,
                }

        if self.can_request:
            if self.is_one_click and self.exam_request.foi:
                return False


def is_request_stale(foirequest):
    last_message = (timezone.now() - foirequest.last_message).days
    return foirequest.awaits_response() and last_message > STALE_THRESHOLD
