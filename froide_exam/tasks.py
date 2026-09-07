import logging
from pathlib import PurePath

from django.conf import settings
from django.contrib.auth import get_user_model

from filingcabinet.models import CollectionDocument
from filingcabinet.utils import ensure_directory_exists, get_existing_directories

from froide.celery import app as celery_app
from froide.document.models import DocumentCollection

from .models import ExamRequest

logger = logging.getLogger(__name__)

User = get_user_model()


@celery_app.task(name="froide_exam.tasks.populate_document_collection", time_limit=60)
def populate_document_collection(collection_id, exam_requests=None):
    collection = DocumentCollection.objects.get(pk=collection_id)
    directories = get_existing_directories(collection)

    if exam_requests:
        exam_requests = ExamRequest.objects.filter(id__in=exam_requests)
    else:
        exam_requests = ExamRequest.objects.filter(documents__isnull=False)

    exam_requests = exam_requests.prefetch_related(
        "documents", "subject", "curriculum", "curriculum__state"
    )

    for er in exam_requests:
        dir_path = PurePath(
            er.curriculum.state.name,
            er.curriculum.name,
            er.subject.name,
            str(er.start_year),
        )
        doc_path = (
            dir_path / "file.pdf"
        )  # ensure_directory_exists creates all parent directories of a file

        directories = ensure_directory_exists(
            collection, directories, doc_path, collection.user
        )

        for document in er.documents.all():
            CollectionDocument.objects.update_or_create(
                defaults={"directory": directories[dir_path]},
                collection=collection,
                document=document,
            )


@celery_app.task(name="froide_exam.tasks.store_exam_uploads")
def store_exam_upload(er_id, upload_urls, user_id):
    from froide.document.services import UploadDocumentStorer

    user = User.objects.get(id=user_id)
    er = ExamRequest.objects.get(id=er_id)

    storer = UploadDocumentStorer(user, public=True)

    all_docs = []

    for upload_url in upload_urls:
        if docs := storer.create_from_upload_url(upload_url):
            all_docs += docs

    er.documents.add(*all_docs)
    populate_document_collection(settings.FROIDE_EXAM_DOCUMENTCOLLECTION, [er_id])
