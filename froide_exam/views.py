from collections import defaultdict

from django.shortcuts import render, get_object_or_404

from froide.publicbody.models import PublicBody

from .models import Curriculum, ExamRequest
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


def curriculum_view(request, curriculum_slug=None):
    curriculum = get_object_or_404(Curriculum, slug=curriculum_slug)

    subjects = curriculum.subjects.all()

    display_years = list(reversed(YEARS))

    for s in subjects:
        s.years = [SubjectYear(subject=s, year=year) for year in display_years]

    exam_requests = ExamRequest.objects.filter(
        curriculum=curriculum
    ).select_related('foirequest')
    exam_request_map = defaultdict(list)
    for er in exam_requests:
        for year in er.get_years():
            exam_request_map[(er.subject_id, year)].append(er)

    default_pb = None

    cu_map = defaultdict(list)
    if not curriculum.publicbody:
        if default_pb is None:
            default_pb = PublicBody.objects.get(
                jurisdiction=curriculum.jurisdictions.all()[0],
                classification__name='Ministerium',
                categories__name='Bildung'
            )
        curriculum.publicbody = default_pb
    min_year, max_year = curriculum.get_min_max_year()
    years = list(range(min_year, max_year + 1))
    for year in years:
        for s in curriculum.subjects.all():
            cu_map[(s.id, year)].append(curriculum)

    for subject in subjects:
        for year in YEARS:
            # This gets the index into reversed years array
            # [2018, 2017, 2016, ...]
            index = abs(year - MAX_YEAR)
            subject_year = subject.years[index]
            subject_year.exam_requests = exam_request_map[(subject.id, year)]
            subject_year.curricula = cu_map[(subject.id, year)]

    return render(request, 'froide_exam/curriculum.html', {
        'years': display_years,
        'subjects': subjects,
        'curriculum': curriculum,
    })
