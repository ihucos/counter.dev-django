# Generated by Django 3.2.12 on 2024-04-01 19:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('scope', models.CharField(choices=[('DAY', 'Day'), ('MONTH', 'Month'), ('YEAR', 'Year'), ('ALL', 'All')], max_length=16)),
                ('browser', models.JSONField()),
                ('country_code', models.JSONField()),
                ('device_type', models.JSONField()),
                ('platform', models.JSONField()),
                ('hour', models.JSONField()),
                ('language', models.JSONField()),
                ('page', models.JSONField()),
                ('referrer', models.JSONField()),
                ('screen_size', models.JSONField()),
                ('weekday_number', models.JSONField()),
                ('domain', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='analytics.domain')),
            ],
        ),
    ]
