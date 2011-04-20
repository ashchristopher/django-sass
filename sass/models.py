from django.db import models
from django.conf import settings
from django.utils.http import urlquote

SASS_ROOT = getattr(settings, 'SASS_ROOT', settings.MEDIA_ROOT)
SASS_URL = getattr(settings, 'SASS_URL', settings.MEDIA_URL)


class SassModel(models.Model):
    name = models.CharField(max_length=60, primary_key=True, help_text='Name of the Sass conversion.')
    sass_path = models.CharField(max_length=255, help_text='Path submitted for the Sass file.')
    css_path = models.CharField(max_length=255, help_text='Path to the generated CSS file.')
    style = models.CharField(choices='', max_length=10, help_text='The style used when creating the css file.')
    source_modified_time = models.CharField(max_length=12, help_text='Last time the source file was modified.')

    def __unicode__(self):
        return self.name

    def relative_css_path(self):
        print self.css_path.split(SASS_ROOT)[1].lstrip('/')
        return self.css_path.split(SASS_ROOT)[1].lstrip('/')

    def css_media_path(self):
        return SASS_URL + urlquote(self.relative_css_path())


from sass import listeners
listeners.start_listening()
