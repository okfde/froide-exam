import json
from collections import defaultdict

from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from froide.foirequest.models import FoiRequest
from froide.helper.email_sending import send_mail
from froide.helper.spam import SpamProtectionMixin

from .forms import ExamUploadForm
from .models import Curriculum, ExamRequest, PrivateCopy, State
from .utils import MAX_YEAR, YEARS, SubjectYear

ALL = "all"


def index(request):
    return redirect("/kampagnen/verschlusssache-pruefung/")


def sent(request):
    request_id = request.GET.get("request")
    request_url = "/a/" + request_id if request_id else "/account/requests/"
    share_url = "https://fragdenstaat.de" + (request_url if request_id else "/vsp")

    return render(
        request,
        "froide_exam/sent.html",
        {"request_url": request_url, "share_url": share_url},
    )


def state_view(request, state_slug=None):
    state = get_object_or_404(State, slug=state_slug)

    all_curricula = Curriculum.objects.filter(state=state)
    types = ({"name": c.name, "slug": c.slug} for c in all_curricula)

    curricula = []
    requested_type = request.GET.get("type")
    if requested_type and requested_type != ALL:
        curricula = list(filter(lambda c: c.slug == requested_type, all_curricula))
    else:
        curricula = all_curricula

    # if no curricula match the request, throw a 404
    # states, that can't be requested don't need curricula to begin with,
    # so we make an exception for them
    if len(curricula) == 0 and state.needs_request():
        raise Http404

    display_years = list(reversed(YEARS))

    all_subjects = []
    for curriculum in curricula:
        subjects = curriculum.subjects.all()

        exam_requests = ExamRequest.objects.filter(
            curriculum=curriculum, documents=None
        ).select_related("foirequest")
        exam_request_map = defaultdict(list)

        same_requests = {}
        if state.is_oneclick() and request.user.is_authenticated:
            foirequest_ids = {er.foirequest_id for er in exam_requests}
            same_requests = {
                fr.same_as_id or fr.id: fr
                for fr in FoiRequest.objects.filter(user=request.user).filter(
                    Q(same_as_id__in=foirequest_ids) | Q(id__in=foirequest_ids)
                )
            }

        for s in subjects:
            s.years = [
                SubjectYear(
                    user=request.user,
                    subject=s,
                    year=year,
                    same_requests=same_requests,
                    state=state,
                )
                for year in display_years
            ]

        for er in exam_requests:
            for year in er.get_years():
                exam_request_map[(er.subject_id, year)].append(er)

        cu_map = defaultdict(list)

        min_year, max_year = curriculum.get_min_max_year()
        years = list(range(min_year, max_year + 1))
        for year in years:
            for s in subjects:
                cu_map[(s.id, year)].append(curriculum)

        for subject in subjects:
            for year in YEARS:
                # This gets the index into reversed years array
                # [2018, 2017, 2016, ...]
                index = abs(year - MAX_YEAR)
                subject_year = subject.years[index]
                subject_year.exam_requests = exam_request_map[(subject.id, year)]
                subject_year.curricula = cu_map[(subject.id, year)]

            subject.curriculum = curriculum
            all_subjects.append(subject)

    return render(
        request,
        "froide_exam/state.html",
        {
            "years": display_years,
            "subjects": all_subjects,
            "state": state,
            "types": types,
            "requested_type": requested_type,
        },
    )


class PrivateCopyForm(SpamProtectionMixin, forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    SPAM_PROTECTION = {"captcha": "ip", "action": "exam-privatecopy"}


def private_copy(request):
    token = request.GET.get("token")
    if token:
        try:
            PrivateCopy.objects.get(token=token)
        except (PrivateCopy.DoesNotExist, ValidationError):
            messages.add_message(request, messages.ERROR, _("Invalid token."))
        else:
            return render(request, "froide_exam/view_private_copy.html")

    if request.method == "POST":
        form = PrivateCopyForm(data=request.POST, request=request)
        if form.is_valid():
            email = form.cleaned_data["email"]

            token = PrivateCopy.objects.create().token
            url = "https://fragdenstaat.de/privatkopie?token={}".format(token)

            message = """Hallo!\r\n\r\n
Hier kannst du die Prüfungsaufgaben einsehen:\r\n
{}\r\n\r\n
Beste Grüße\r\n
Das Team von FragDenStaat""".format(url)

            send_mail(
                subject=_("Exam questions"),
                body=message,
                email_address=email,
                fail_silently=False,
            )

            messages.add_message(
                request, messages.SUCCESS, _("We have sent you an email.")
            )
    else:
        form = PrivateCopyForm(request=request)
    return render(
        request, "froide_exam/request_private_copy.html", context={"form": form}
    )


def upload_exams(request):
    from froide.upload.forms import get_uppy_i18n

    if not request.user.has_perm("froide_exam.add_examrequest"):
        raise PermissionDenied

    if request.method == "POST":
        form = ExamUploadForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            messages.add_message(
                request,
                messages.SUCCESS,
                _("Exams added."),
            )
            return redirect(request.get_full_path())
    else:
        form = ExamUploadForm()

    config = json.dumps(
        {
            "settings": {
                "tusChunkSize": settings.DATA_UPLOAD_MAX_MEMORY_SIZE - (500 * 1024)
            },
            "i18n": {
                "uppy": get_uppy_i18n(),
            },
            "url": {
                "tusEndpoint": reverse("api:upload-list"),
            },
        }
    )

    return render(request, "froide_exam/upload.html", {"form": form, "config": config})
