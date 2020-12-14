from django.db import migrations

def create_states(apps, schema_editor):
    states = [
      # name, slug, juris, public body, legal status
      ('Baden-Württemberg', 'baden-wuerttemberg', [91], 8976, 'unrequestable'),
      ('Bayern', 'bayern', [92], 11210, 'request_not_publish'),
      ('Berlin und Brandenburg', 'berlin-brandenburg', [3, 4], 3919, 'unrequestable'),
      ('Bremen', 'bremen', [12], 6667, 'request'),
      ('Hamburg', 'hamburg', [5], 3986, 'request'),
      ('Hessen', 'hessen', [94], 9924, 'unrequestable'),
      ('Mecklenburg-Vorpommern', 'mecklenburg-vorpommern', [7], 5142, 'requestable'),
      ('Niedersachsen', 'niedersachsen', [93], 10283, 'requestable'),
      ('Nordrhein-Westfalen', 'nrw', [2], 3009, 'request_not_publish'),
      ('Rheinland-Pfalz', 'rheinland-pfalz', [6], 14403, 'unrequestable'),
      ('Saarland', 'saarland', [9], 6172, 'unrequestable'),
      ('Sachsen', 'sachsen', [89], 10896, 'unrequestable'),
      ('Sachsen-Anhalt', [13], 14737, 'request'),
      ('Schleswig-Holstein', [11], 7666, 'request'),
      ('Thüringen', [10], 7007, 'unrequestable'),
    ]

    from ..models import Jurisdiction

    State = apps.get_model('froide_exam', 'State')
    Curriculum = apps.get_model('froide_exam', 'Curriculum')
    
    for name, slug, juris, pb, legal in states:
        jurisdictions = list(map(lambda id: Jurisdiction.objects.get(id=id), juris))

        state = State(
            name=name,
            slug=slug,
            publicbody_id=pb,
            legal_status=legal
        )
        state.save()
        state.jurisdictions.set(juris)
        state.save()
        
        curriculum = Curriculum.objects.get(slug=slug)
        curriculum.state = state.id
        curriculum.save()

    

class Migration(migrations.Migration):
    dependencies = [
      ('froide_exam', '0011_add_states'),
    ]

    operations = [
      migrations.RunPython(create_states),
    ]