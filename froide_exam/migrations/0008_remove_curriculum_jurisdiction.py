# Generated by Django 2.1.5 on 2019-02-08 11:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('froide_exam', '0007_auto_20190208_1158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='curriculum',
            name='jurisdiction',
        ),
    ]