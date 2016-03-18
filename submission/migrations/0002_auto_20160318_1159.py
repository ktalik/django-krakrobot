# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('submission', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='result',
            name='submission_id',
        ),
        migrations.AddField(
            model_name='result',
            name='submission',
            field=models.ForeignKey(default=0, to='submission.Submission'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='team',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
