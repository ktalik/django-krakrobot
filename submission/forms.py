from django import forms
from django.template.defaultfilters import filesizeformat
from django.utils.translation import ugettext_lazy as _


class ContentTypeRestrictedFileField(forms.FileField):
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
        file = super(ContentTypeRestrictedFileField, self).clean(*args, **kwargs)
        try:
            content_type = file.content_type
            print "Submission content type: {}".format(content_type)
            if content_type in self.content_types:
                print "Submission file size: {}".format(file._size)
                if file._size > self.max_upload_size:
                    raise forms.ValidationError(
                        _('Please keep filesize under %(size_limit)s. Current filesize %(current_size)s'),
                        params={
                            'size_limit': filesizeformat(self.max_upload_size),
                            'current_size': filesizeformat(file._size)
                        }
                    )
            else:
                raise forms.ValidationError(
                    _("Filetype '%(current_type)s' is not supported."),
                    params={
                        'current_type': file.content_type
                    }
                )
        except AttributeError:
            raise

        return file


class UploadSubmissionForm(forms.Form):
    file  = ContentTypeRestrictedFileField(
        content_types=['application/zip', 'application/x-zip-compressed', 'application/x-tar', 'application/x-gtar', 'binary/octet-stream'],
        max_upload_size=1310720,
    )

