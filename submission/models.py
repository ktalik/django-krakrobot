from django.db import models
from django.contrib.auth.models import User


DB_NAME_LENGTH = 100


class Team(models.Model):
    name = models.CharField(max_length=DB_NAME_LENGTH)
    user = models.ForeignKey(User)
    passed = models.BooleanField()

    def __unicode__(self):  # Python 3: def __str__(self):
        return self.name


class Submission(models.Model):
    api_id = models.IntegerField()
    team = models.ForeignKey(Team)
    code = models.TextField()

    def __unicode__(self):  # Python 3: def __str__(self):
        return unicode(self.api_id) + ' - submitted by: ' + unicode(self.team)


class Result(models.Model):
    api_id = models.IntegerField()
    result = models.CharField(max_length=1000)

    def __unicode__(self):  # Python 3: def __str__(self):
        return unicode(self.api_id) + ' - with result: ' + unicode(self.result)

