# Generated by Django 3.1.4 on 2021-01-18 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('froide_exam', '0013_allow_blank_juris'),
    ]

    operations = [
        migrations.AlterField(
            model_name='curriculum',
            name='slug',
            field=models.SlugField(default='abitur'),
            preserve_default=False,
        ),
    ]
