# Generated by Django 3.0.2 on 2020-01-30 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20200130_0308'),
    ]

    operations = [
        migrations.AddField(
            model_name='lab',
            name='name',
            field=models.CharField(default='SSP9', max_length=30),
            preserve_default=False,
        ),
    ]