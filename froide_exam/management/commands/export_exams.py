from django.core.management.base import BaseCommand

from froide_exam.models import ExamRequest
from froide.foirequest.models import FoiAttachment

import zipfile


class Command(BaseCommand):
    help = "Export exam files"

    def add_arguments(self, parser):
        parser.add_argument("output_file")

    def get_files(self):
        exam_requests = ExamRequest.objects.filter(
            foirequest__isnull=False
        ).select_related("foirequest", "subject", "curriculum", "curriculum__state")

        i = 0
        count = exam_requests.count()

        for exam in exam_requests:
            attachments = FoiAttachment.objects.filter(
                belongs_to__request=exam.foirequest, is_redacted=False
            )

            # create a zip file with the following structure:
            # {state_name}/{subject_name}/{year}/{request_pk}/{attachment_name}

            for attachment in attachments:
                year = str(exam.start_year.year)
                zip_path = "/".join(
                    [
                        exam.curriculum.state.name,
                        exam.curriculum.name,
                        exam.subject.name,
                        year,
                        str(exam.foirequest.pk),
                        attachment.name,
                    ]
                )

                yield attachment.file.path, zip_path

            if i % 10:
                print(f"{i} / {count} \t {i / count * 100:.2f}%")

            i += 1

    def handle(self, *args, **options):
        with zipfile.ZipFile(options["output_file"], "w", zipfile.ZIP_DEFLATED) as zipf:
            for source_path, zip_internal_path in self.get_files():
                zipf.write(source_path, zip_internal_path)

        print("Done.")
