from collections import defaultdict

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import Http404

from froide.foirequest.models import FoiRequest
from froide.publicbody.models import PublicBody

from .models import State, Curriculum, ExamRequest, KIND_CHOICES
from .utils import SubjectYear, MAX_YEAR, YEARS


def index(request):
    return redirect('/kampagnen/frag-sie-abi/')
    # curricula = Curriculum.objects.all().prefetch_related(
    #     'jurisdictions', 'subjects'
    # )
    # jurisdictions = set(j for c in curricula for j in c.jurisdictions.all())
    # jurisdictions = sorted(jurisdictions, key=lambda x: (x.rank, x.name))
    # juris_map = defaultdict(list)
    # for c in curricula:
    #     for j in c.jurisdictions.all():
    #         juris_map[j].append(c)
    # for j, c_list in juris_map.items():
    #     j.curricula = c_list

    # return render(request, 'froide_exam/index.html', {
    #     'jurisdictions': jurisdictions
    # })


def curriculum_view(request, state_slug=None):
    state = get_object_or_404(State, slug=state_slug)
    
    KIND_IDS = list(map(lambda c: c[0], KIND_CHOICES))
    requested_kind = request.GET.get('kind')
    requested_kind = requested_kind if requested_kind in KIND_IDS else False
    
    curricula = []

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

        curriculum.kindText = list(filter(lambda kind: kind[0] == curriculum.kind, KIND_CHOICES))[0][1]

    kinds = []
    for kind in KIND_CHOICES:
        kinds.append({ 'value': kind[0], 'text': kind[1] })

    return render(request, 'froide_exam/curriculum.html', {
        'years': display_years,
        'subjects': subjects_done,
        'state': state,
        'kinds': kinds,
        'requested_kind': requested_kind
    })
