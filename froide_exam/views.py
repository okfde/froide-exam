from collections import defaultdict

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from froide.foirequest.models import FoiRequest
from froide.publicbody.models import PublicBody

from .models import State, Curriculum, ExamRequest, KINDS
from .utils import SubjectYear, MAX_YEAR, YEARS


def index(request):
    return redirect('/kampagnen/verschlusssache-pruefung/')

def state_view(request, state_slug=None):
    state = get_object_or_404(State, slug=state_slug)
    
    # check if ?kind=... is ok
    kind_ids = KINDS.keys()
    requested_kind = request.GET.get('kind')
    requested_kind = requested_kind if requested_kind in kind_ids else False
    
    # TODO: remove on launch!
    # this emulates the old FragSieAbi site and only allows Abitur requests
    requested_kind = 'abitur'
    
    curricula = []

    # TODO: better way to this?
    if requested_kind:
        curricula = Curriculum.objects.filter(state=state, kind=requested_kind)
    else:
        curricula = Curriculum.objects.filter(state=state)
    
    display_years = list(reversed(YEARS))

    subjects_done = []

    for curriculum in curricula:
        subjects = curriculum.subjects.all()

        exam_requests = ExamRequest.objects.filter(
            curriculum=curriculum
        ).select_related('foirequest')
        exam_request_map = defaultdict(list)

        same_requests = {}
        if state.is_oneclick() and request.user.is_authenticated:
            foirequest_ids = {
                er.foirequest_id for er in exam_requests
            }
            same_requests = {
                fr.same_as_id or fr.id: fr for fr in FoiRequest.objects.filter(
                    user=request.user).filter(
                    Q(same_as_id__in=foirequest_ids) |
                    Q(id__in=foirequest_ids)
                )
            }

        for s in subjects:
            s.years = [
                SubjectYear(
                    user=request.user, subject=s, year=year,
                    same_requests=same_requests
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
                subject_year.state = state
            
            subject.curriculum = curriculum
            subjects_done.append(subject)

        curriculum.kindText = KINDS[curriculum.kind]

    # TODO: remove before launch!
    # this emulates the old FragSieAbi site and only allows Abitur requests
    OVERWRITE_KINDS = {
        'abitur': 'Abitur'
    }

    return render(request, 'froide_exam/state.html', {
        'years': display_years,
        'subjects': subjects_done,
        'state': state,
        'kinds': OVERWRITE_KINDS, # TODO: remove before launch!
        'requested_kind': requested_kind
    })
