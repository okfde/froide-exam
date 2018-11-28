import functools
from collections import defaultdict

from django.shortcuts import render, get_object_or_404

from froide.publicbody.models import Jurisdiction, PublicBody

from .models import Curriculum, ExamRequest
from .utils import SubjectYear, MIN_YEAR, YEARS


def index(request):
    curricula = Curriculum.objects.all().prefetch_related(
        'jurisdiction', 'subjects'
    )
    jurisdictions = set(c.jurisdiction for c in curricula)
    jurisdictions = sorted(jurisdictions, key=lambda x: (x.rank, x.name))
    juris_map = defaultdict(list)
    for c in curricula:
        juris_map[c.jurisdiction].append(c)
    for j, c_list in juris_map.items():
        j.curricula = c_list

    return render(request, 'froide_exam/index.html', {
        'jurisdictions': jurisdictions
    })


def jurisdiction_view(request, jurisdiction_slug=None):
    juris = get_object_or_404(Jurisdiction, slug=jurisdiction_slug)
    curricula = Curriculum.objects.filter(
        jurisdiction=juris
    ).prefetch_related('subjects', 'publicbody')

    subjects = functools.reduce(lambda a, b: a | b, set(
        c.subjects.all() for c in curricula))
    subjects = sorted(subjects, key=lambda x: x.name)
    for s in subjects:
        s.years = [SubjectYear(subject=s, year=year) for year in YEARS]

    exam_requests = ExamRequest.objects.filter(
        curriculum_id__in=curricula
    ).select_related('foirequest')
    exam_request_map = defaultdict(list)
    for er in exam_requests:
        exam_request_map[(er.subject_id, er.year.year)].append(er)

    default_pb = None

    cu_map = defaultdict(list)
    for c in curricula:
        if not c.publicbody:
            if default_pb is None:
                default_pb = PublicBody.objects.get(
                    jurisdiction=c.jurisdiction,
                    classification__name='Ministerium',
                    categories__name='Bildung'
                )
            c.publicbody = default_pb
        min_year, max_year = c.get_min_max_year()
        years = list(range(min_year, max_year + 1))
        for year in years:
            for s in c.subjects.all():
                cu_map[(s.id, year)].append(c)

    for subject in subjects:
        for year in YEARS:
            index = year - MIN_YEAR
            subject_year = subject.years[index]
            subject_year.exam_requests = exam_request_map[(subject.id, year)]
            subject_year.curricula = cu_map[(subject.id, year)]

    return render(request, 'froide_exam/jurisdiction.html', {
        'years': list(reversed(YEARS)),
        'juris': juris,
        'subjects': subjects,
    })
