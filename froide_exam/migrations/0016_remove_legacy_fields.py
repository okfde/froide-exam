# Generated by Django 3.1.6 on 2021-03-16 13:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('froide_exam', '0015_privatecopy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='curriculum',
            name='content_placeholder',
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='description',
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='jurisdictions',
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='kind',
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