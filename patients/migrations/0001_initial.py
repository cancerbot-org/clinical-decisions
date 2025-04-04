from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_id', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('date_of_birth', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Diagnostic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cbc', models.JSONField(default=dict)),
                ('calcium', models.FloatField(blank=True, null=True)),
                ('creatinine', models.FloatField(blank=True, null=True)),
                ('beta2_microglobulin', models.FloatField(blank=True, null=True)),
                ('ldh', models.FloatField(blank=True, null=True)),
                ('imaging_results', models.JSONField(default=dict)),
                ('biomarkers', models.JSONField(default=dict)),
                ('date', models.DateField(auto_now_add=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Monitoring',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('m_protein', models.FloatField(blank=True, null=True)),
                ('mrD_status', models.CharField(max_length=50)),
                ('symptoms', models.JSONField(default=list)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.patient')),
            ],
        ),
    ]