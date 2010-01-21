import sys,os
from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.core.management.color  import no_style

from commands import getstatusoutput

class Command(NoArgsCommand):
    requires_model_validation = False
    can_import_settings = True
    style = no_style()
    
    def handle_noargs(self, **kwargs):
        # cmd = 'find %s -name "*.pyc" -exec rm {} \;' %(settings.PROJECT_PATH)
        # (status, output) = getstatusoutput(cmd)
        # if not status == 0:
        #     import sys
        #     sys.stderr.write("%s\n" %(output))
        
        try:
            bin = settings.SASS_BIN
        except:
            sys.stderr.write(self.style.ERROR('SASS_BIN is not defined in settings.py file.\n'))
            return
            
        # test that binary defined exists
        if not os.path.exists(bin):
            sys.stderr.write(self.style.ERROR('Sass binary defined by SASS_BIN does not exist: %s\n' %bin))
            return
        
        