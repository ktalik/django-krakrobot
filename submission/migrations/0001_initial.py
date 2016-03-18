# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import submission.models
import django.utils.timezone
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('submission_id', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('report', models.CharField(default=b'{}', max_length=1000)),
                ('log', models.CharField(default=b'', max_length=10000)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('package', models.FileField(null=True, upload_to=submission.models.submission_directory_path, blank=True)),
                ('command', models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('passed', models.BooleanField(default=False)),
                ('avatar', models.ImageField(null=True, upload_to=b'avatars', blank=True)),
                ('registration_code', models.CharField(default=submission.models.generate_code, max_length=32, blank=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='submission',
            name='team',
            field=models.ForeignKey(to='submission.Team'),
        ),
        migrations.AddField(
            model_name='submission',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
