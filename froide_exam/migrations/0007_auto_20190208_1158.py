# Generated by Django 2.1.5 on 2019-02-08 10:58

from django.db import migrations


def move_jurisdiction(apps, schema_editor):
    Curriculum = apps.get_model('froide_exam', 'Curriculum')
    for cur in Curriculum.objects.all():
        if cur.jurisdiction:
            cur.jurisdictions.add(cur.jurisdiction)


class Migration(migrations.Migration):

    dependencies = [
        ('froide_exam', '0006_auto_20190208_1153'),
    ]

    operations = [
        migrations.RunPython(move_jurisdiction)
    ]