from collections import defaultdict

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import Http404

from froide.foirequest.models import FoiRequest
from froide.publicbody.models import PublicBody

from .models import State, Curriculum, ExamRequest
from .utils import SubjectYear, MAX_YEAR, YEARS

ALL = 'all'

def index(request):
    return redirect('/kampagnen/verschlusssache-pruefung/')

def sent(request):
    request_id = request.GET.get('request')
    request_url = '/a/' + request_id if request_id else '/account/requests/'
    share_url = 'https://fragdenstaat.de' + (request_url if request_id else '/vsp')
    
    return render(request, 'froide_exam/sent.html', {
        'request_url': request_url,
        'share_url': share_url
    })

def state_view(request, state_slug=None):
    state = get_object_or_404(State, slug=state_slug)
    
    all_curricula = Curriculum.objects.filter(state=state)
    types = map(lambda c: { 'name': c.name, 'slug': c.slug }, all_curricula)

    curricula = []
    requested_type = request.GET.get('type')
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
            all_subjects.append(subject)

    return render(request, 'froide_exam/state.html', {
        'years': display_years,
        'subjects': all_subjects,
        'state': state,
        'types': types,
        'requested_type': requested_type
    })
