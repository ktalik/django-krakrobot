import time
import uuid

from django.db import models
from django.template.defaultfilters import filesizeformat
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import forms


DB_NAME_LENGTH = 100


class ContentTypeRestrictedFileField(models.FileField):
    """
    Same as FileField, but you can specify:
        * content_types - list containing allowed content_types. Example: ['application/pdf', 'image/jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            1.25MB - 1310720
            2.5MB  - 2621440
            5MB    - 5242880
            10MB   - 10485760
            20MB   - 20971520
            50MB   - 5242880
            100MB  - 104857600
            250MB  - 214958080
            500MB  - 429916160
    """
    def __init__(self, *args, **kwargs):
        self.content_types = []
        self.max_upload_size = 1310720
        if 'content_types' in kwargs:
            self.content_types = kwargs.pop("content_types")
        if 'max_upload_size' in kwargs:
            self.max_upload_size = kwargs.pop("max_upload_size")

        super(ContentTypeRestrictedFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)

        file = data.file
        try:
            content_type = file.content_type
            if content_type in self.content_types:
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(_('Please keep filesize under %s. Current filesize %s') % (filesizeformat(self.max_upload_size), filesizeformat(file._size)))
            else:
                raise forms.ValidationError(_('Filetype not supported.'))
        except AttributeError:
            pass

        return data


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
    #package = models.FileField(upload_to=submission_directory_path)
    package = ContentTypeRestrictedFileField(
        upload_to=submission_directory_path,
        content_types=['application/zip'],
        max_upload_size=1310720,
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


