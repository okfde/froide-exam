from pathlib import PurePath

from filingcabinet.models import CollectionDirectory, CollectionDocument
from filingcabinet.utils import ensure_directory_exists, get_existing_directories

from froide.celery import app as celery_app
from froide.document.models import DocumentCollection

from .models import ExamRequest


@celery_app.task(name="froide_exam.tasks.populate_document_collection", time_limit=60)
def populate_document_collection(collection_id):
    collection = DocumentCollection.objects.get(pk=collection_id)
    directories = get_existing_directories(collection)

    exam_requests = ExamRequest.objects.filter(
        documents__isnull=False
    ).prefetch_related("documents", "subject", "curriculum", "curriculum__state")

    used_directories = set()
    used_collection_documents = set()

    for er in exam_requests:
        dir_path = PurePath(
            er.curriculum.state.name,
            er.curriculum.name,
            er.subject.name,
            str(er.start_year.year),
        )
        doc_path = (
            dir_path / "file.pdf"
        )  # ensure_directory_exists creates all parent directories of a file

        directories = ensure_directory_exists(
            collection, directories, doc_path, collection.user
        )
        for path in doc_path.parents:
            if path != PurePath("."):
                used_directories.add(directories[path].id)

        for document in er.documents.all():
            collection_document, _created = CollectionDocument.objects.update_or_create(
                defaults={"directory": directories[dir_path]},
                collection=collection,
                document=document,
            )

            used_collection_documents.add(collection_document.id)

    CollectionDirectory.objects.filter(collection=collection).exclude(
        id__in=used_directories
    ).delete()
    CollectionDocument.objects.filter(collection=collection).exclude(
        id__in=used_collection_documents
    ).delete()
