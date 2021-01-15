# Generated by Django 3.1.4 on 2021-01-13 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('froide_exam', '0012_populate_states'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='jurisdictions',
            field=models.ManyToManyField(blank=True, related_name='curriculums', to='publicbody.Jurisdiction'),
        ),
    ]