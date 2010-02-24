import os

from django.db.models import signals
from django.conf import settings

from sass.models import SassModel



def set_last_modified_time(sender, instance, **kwargs):
    # set the last modified time based on the os.stat system call.
    st_mtime = 8  # last_modified_time column
    print os.stat(instance.css_path)[8]
    


def start_listening():
    signals.pre_save.connect(set_last_modified_time, sender=SassModel)