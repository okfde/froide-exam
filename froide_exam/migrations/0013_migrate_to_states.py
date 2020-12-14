import cms.models.fields
from django.db import migrations, models
import django.db.models.deletion


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
