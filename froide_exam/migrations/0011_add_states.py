import cms.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('publicbody', '0031_publicbody_change_history'),
        ('cms', '0022_auto_20180620_1551'),
        ('froide_exam', '0010_auto_20201119_1718'),
    ]

    operations = [
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('slug', models.SlugField()),
                ('legal_status', models.CharField(choices=[('request', 'Anfragbar'), ('request_not_publish', 'Anfragbar (nicht veröffentlichbar)'), ('public', 'Schon öffentlich'), ('unrequestable', 'Nicht anfragbar')], default='request', max_length=100)),
                ('description', models.TextField(blank=True)),
                ('jurisdictions', models.ManyToManyField(related_name='curriculums', to='publicbody.Jurisdiction')),
                ('publicbody', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='publicbody.PublicBody')),
            ],
            options={
                'verbose_name': 'state',
                'verbose_name_plural': 'states',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='curriculum',
            name='state',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='state', to='froide_exam.State'),
        ),
    ]
