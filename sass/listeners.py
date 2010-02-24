from django.db.models import signals

from sass.models import SassModel

def determine_media_url(sender, instance, **kwargs):
    instance.source_modified_time = '12345'


def start_listening():
    print 'Starting listeners'
    signals.pre_save.connect(determine_media_url, sender=SassModel)