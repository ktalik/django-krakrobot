import time
import uuid
import shutil
import os

from django.db import models
from django.template.defaultfilters import filesizeformat
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import forms


DB_NAME_LENGTH = 100

def generate_code():
    uid = uuid.uuid4()
    return uid.hex

class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=DB_NAME_LENGTH)
    user = models.ForeignKey(User, null=True, blank=True)
    passed = models.BooleanField(blank=True, default=False)
    avatar = models.ImageField(upload_to='avatars', null=True, blank=True)
    registration_code = models.CharField(max_length=32, default=generate_code, blank=True)

    def __unicode__(self):
        return self.name

    def regenerate_code(self):
        self.registration_code = generate_code()


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

    def delete(self, *args, **kwargs):
        for result in Result.objects.filter(submission_id__exact = self.id):
            result.delete()
        dir_path = os.path.dirname(self.package.path)
        print "Submission directory path to delete: {}".format(dir_path)
        shutil.rmtree(dir_path, ignore_errors=True)
        super(Submission, self).delete(*args, **kwargs)


class Result(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission_id = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    report = models.CharField(max_length=1000, default='{}')
    log = models.CharField(max_length=10000, default='')

    def __unicode__(self):
        return unicode(self.id) + ' - with report: ' + unicode(self.report)


