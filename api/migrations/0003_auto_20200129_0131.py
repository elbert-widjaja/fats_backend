# Generated by Django 3.0.2 on 2020-01-28 17:31

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20200129_0101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='schedule',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
