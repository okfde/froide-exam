# Generated by Django 3.0.8 on 2020-12-18 15:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('froide_exam', '0012_populate_states'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='curriculum',
            name='content_placeholder',
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='jurisdictions',
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='legal_status',
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='publicbody',
        ),
    ]
