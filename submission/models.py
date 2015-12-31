import time
import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


DB_NAME_LENGTH = 100


class Team(models.Model):
    name = models.CharField(max_length=DB_NAME_LENGTH)
    user = models.ForeignKey(User)
    passed = models.BooleanField()

    def __unicode__(self):
        return self.name


class Submission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    team = models.ForeignKey(Team)
    code = models.TextField()
    date = models.DateTimeField(default=timezone.now)

    def __unicode__(self):
        return unicode(self.date) + ' ' + unicode(self.id) + \
            ' - submitted by: ' + unicode(self.team)


class Result(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report = models.CharField(max_length=1000, default='{}')
    log = models.CharField(max_length=10000, default='')

    def __unicode__(self):
        return unicode(self.id) + ' - with report: ' + unicode(self.report)

