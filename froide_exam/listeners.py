from datetime import datetime
from django.utils import timezone

from froide.foirequest.models import FoiAttachment

from .models import ExamRequest, Subject, Curriculum
from .utils import REFERENCE_NAMESPACE, is_request_stale


def from_reference(reference):
    try:
        namespace, curriculum_id, subject_id, year = reference.split(':', 3)
    except ValueError:
        return

    try:
        subject = Subject.objects.get(pk=subject_id)
    except Subject.DoesNotExist:
        return

    try:
        curriculum = Curriculum.objects.get(pk=curriculum_id)
    except Curriculum.DoesNotExist:
        return

    try:
        year = int(year)
        if not curriculum.is_valid_year(year):
            return
    except ValueError:
        return

    return curriculum, subject, year


def connect_request_object(sender, **kwargs):
    reference = kwargs.get('reference')
    if not reference:
        return
    if not reference.startswith(REFERENCE_NAMESPACE):
        return

    result = from_reference(reference)
    if result is None:
        return
    curriculum, subject, year = result

    sender.user.tags.add('exam')
    if not sender.user.is_active:
        # First-time requester
        sender.user.tags.add('exam-first')

    year_date = timezone.make_aware(datetime(year, 1, 1))

    er = ExamRequest.objects.filter(
        curriculum=curriculum,
        subject=subject,
        start_year=year_date
    ).first()

    if not er or is_request_stale(er.foirequest):
        # there already is an existing exam request
        # since it's stale however, we'll abandon the old one
        # and add a new one. we won't overwrite the old one,
        # so it is still marked as a pending request for the
        # original requester in the interface.
        ExamRequest.objects.create(
            curriculum=curriculum,
            subject=subject,
            start_year=year_date,
            timestamp=sender.created_at,
            foirequest=sender,
        )

    if curriculum.state.is_oneclick():
        sender.not_publishable = True
        sender.save()


def hide_attachments(sender=None, message=None, **kwargs):
    if not sender.reference.startswith(REFERENCE_NAMESPACE):
        return

    result = from_reference(sender.reference)
    if result is None:
        return
    curriculum, subject, year = result

    if not curriculum.state.is_oneclick():
        return

    FoiAttachment.objects.filter(
        belongs_to=message, filetype__contains='pdf'
    ).update(
        can_approve=False
    )
