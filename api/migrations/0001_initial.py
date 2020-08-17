# Generated by Django 3.0.2 on 2020-01-28 13:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('course_id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('desc', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Lab',
            fields=[
                ('index', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('user_id', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=30)),
                ('email', models.EmailField(max_length=254)),
                ('password', models.CharField(max_length=30)),
                ('time_added', models.DateTimeField(auto_now_add=True)),
                ('courses', models.ManyToManyField(to='api.Course')),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField()),
                ('attendees', models.ManyToManyField(to='api.Student')),
                ('lab', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Lab')),
            ],
        ),
        migrations.AddField(
            model_name='lab',
            name='students',
            field=models.ManyToManyField(to='api.Student'),
        ),
    ]
