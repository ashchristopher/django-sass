import sys,os
from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.core.management.color  import no_style

from commands import getstatusoutput

class SassConfigException(Exception):
    pass

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
            
        try:
            sass_definitions = settings.SASS
        except:
            sass_definitions = ()
            
        for sass_def in sass_definitions:
            try:
                sass_name = sass_def.get('name', None)
                sass_details = sass_def.get('details', {})
                sass_input = sass_details.get('input', None)
                sass_output = sass_details.get('output', None)
                
                # i hate generic exception message - try to give the user a meaningful message about what exactly the problem is.
                for prop in [('name', sass_name), ('details', sass_details), ('input', sass_input), ('output', sass_output)]:
                    if not prop[1]:
                        raise SassConfigException('Sass \'%s\' property not defined in configuration:\n%s\n' %(prop[0], sass_def))                
                self.process_sass(sass_name, sass_input, sass_output)
            except SassConfigException, e:
                sys.stderr.write(self.style.ERROR(e.message))
            
    def process_sass(self, name, sass_input, css_output):
        print 'Converting %s to %s' %(sass_input, css_output)
    
    def get_sass_file_path(self, relative_path):
        site_media = settings.MEDIA_ROOT
        
        