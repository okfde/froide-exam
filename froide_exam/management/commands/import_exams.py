import unicodedata
import zipfile
from collections import defaultdict
from datetime import date
from pathlib import PurePath

from django.core.management.base import BaseCommand
from django.db import transaction

from filingcabinet.services import ZIP_BLOCK_LIST, trigger_process_document_task

from froide.document.models import Document

from ...models import Curriculum, ExamRequest, Subject


def fix_encoding(text):
    return unicodedata.normalize("NFC", text.encode("cp437").decode("utf-8"))


class Command(BaseCommand):
    help = "Import sorted exams as documents"

    def add_arguments(self, parser):
        parser.add_argument("input_file")
        parser.add_argument("user_id")

    def handle(self, *args, **options):
        documents = defaultdict(list)

        subjects = {s.name: s for s in Subject.objects.all()}
        curricula = defaultdict(dict)

        for curriculum in Curriculum.objects.prefetch_related("state").all():
            curricula[curriculum.state.name][curriculum.name] = curriculum

        with zipfile.ZipFile(options["input_file"], "r") as zf:
            zip_paths = []

            for zip_info in zf.infolist():
                path = PurePath(zip_info.filename)
                parts = path.parts
                if parts[0] in ZIP_BLOCK_LIST:
                    continue

                if path.suffix == ".pdf":
                    zip_paths.append(path)

            print("Found", len(zip_paths), "PDFs")

            for path in zip_paths:
                parts = [fix_encoding(part) for part in path.parts]
                state = parts[0]
                curriculum = parts[1]
                subject = parts[2]
                year = parts[3]
                filename = parts[-1]

                description = (
                    f"{curriculum}-Prüfung in {state} aus {year} in {subject} "
                )

                data = {
                    "state": curricula[state][curriculum].state.id,
                    "curriculum": curricula[state][curriculum].id,
                    "subject": subjects[subject].id,
                    "year": year,
                }

                document = Document.objects.create(
                    title=filename.replace(".pdf", ""),
                    description=description,
                    user_id=int(options["user_id"]),
                    data=data,
                    public=True,
                    pending=True,
                )
                documents[(state, curriculum, subject, year)].append(document)

                document.pdf_file.save(filename, zf.open(str(path)), save=True)
                transaction.on_commit(trigger_process_document_task(document.pk))

                print(f"Imported {filename}", document.pk)

        for (state, curriculum, subject, year), docs in documents.items():
            exam_request = ExamRequest.objects.create(
                curriculum=curricula[state][curriculum],
                subject=subjects[subject],
                start_year=date(int(year), 1, 1),
            )

            exam_request.documents.set(docs)
            exam_request.save()
            print(f"Created {exam_request}", exam_request.pk)

        print("Done.")
