from django.db import migrations

def create_states(apps, schema_editor):
    from ..models import Jurisdiction

    State = apps.get_model('froide_exam', 'State')
    Curriculum = apps.get_model('froide_exam', 'Curriculum')

    for curriculum in Curriculum.objects.all():
        state = State(
            name=curriculum.name,
            slug=curriculum.slug,
            publicbody=curriculum.publicbody,
            legal_status=curriculum.legal_status
        )
        state.save()

        curriculum.state = state
        curriculum.save()
class Migration(migrations.Migration):
    dependencies = [
      ('froide_exam', '0011_auto_20201218_1323'),
    ]

    operations = [
      migrations.RunPython(create_states, atomic=False),
    ]