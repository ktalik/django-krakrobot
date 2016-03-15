import time
import uuid

from django.db import models
from django.template.defaultfilters import filesizeformat
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import forms


DB_NAME_LENGTH = 100


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=DB_NAME_LENGTH)
    user = models.ForeignKey(User)
    passed = models.BooleanField()
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True)

    def __unicode__(self):
        return self.name


def submission_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/submissions/<id>/<filename>
    return 'submissions/{0}/{1}'.format(instance.id, filename)


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team)
    user = models.ForeignKey(User)
    date = models.DateTimeField(default=timezone.now)
    package = models.FileField(
        upload_to=submission_directory_path,
        blank=True,
        null=True
    )
    # User-specified command for code execution
    command = models.CharField(max_length=1000)

    def __unicode__(self):
        return unicode(self.date) + ' ' + unicode(self.id) + \
            ' - submitted by: ' + unicode(self.team)


class Result(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission_id = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    report = models.CharField(max_length=1000, default='{}')
    log = models.CharField(max_length=10000, default='')

    def __unicode__(self):
        return unicode(self.id) + ' - with report: ' + unicode(self.report)


