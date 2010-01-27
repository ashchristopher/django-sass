import sys,os
from optparse import make_option

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management.color  import no_style

from commands import getstatusoutput

class SassConfigException(Exception):
    pass

class Command(BaseCommand):
    requires_model_validation = False
    can_import_settings = True
    style = no_style()
    
    option_list = BaseCommand.option_list + ( 
        make_option('--style', '-t', dest='sass_style', default='nested', help='Sass output style. Can be nested (default), compact, compressed, or expanded.'),
        make_option('--list', '-l', action='store_true', dest='list_sass' , default=None, help='Display information about the status of your sass files.'),
    )
    help = 'Converts Sass files into CSS.'
    
    
    def handle(self, **kwargs):
        # cmd = 'find %s -name "*.pyc" -exec rm {} \;' %(settings.PROJECT_PATH)
        # (status, output) = getstatusoutput(cmd)
        # if not status == 0:
        #     import sys
        #     sys.stderr.write("%s\n" %(output))
        try:
            self.bin = settings.SASS_BIN
            # test that binary defined exists
            if not os.path.exists(self.bin):
                sys.stderr.write(self.style.ERROR('Sass binary defined by SASS_BIN does not exist: %s\n' %bin))
                return
        except:
            sys.stderr.write(self.style.ERROR('SASS_BIN is not defined in settings.py file.\n'))
            return
        
        # make sure the Sass style given is valid.
        self.sass_style = kwargs.get('sass_style')
        if self.sass_style not in ('nested', 'compact', 'compressed', 'expanded'):
            sys.stderr.write(self.style.ERROR("Invalid sass style argument: %s\n") %self.sass_style)
            return
        
        if kwargs.get('list_sass'):
            self.process_sass_list()
        else:
            # self.process_sass_files()
            pass
    
    
    def process_sass_list(self):
        print self.build_sass_structure()

            
            
        
        
    def build_sass_structure(self):
        try:
            sass_definitions = settings.SASS
        except:
            sass_definitions = ()
            
        sass_struct = []
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
            except SassConfigException, e:
                sys.stderr.write(self.style.ERROR(e.message))
                return
            sass_input_root = self.get_file_path(sass_input)
            sass_output_root = self.get_file_path(sass_output)
            sass_struct.append({
                'name' : sass_name,
                'input' : sass_input_root,
                'output' : sass_output_root,
            })
        return sass_struct    
            
            
    # def process_sass_dir(self, name, sass_input, css_output):
    #     """
    #         The user may whish to keep their sass files in their MEDIA_ROOT directory,
    #         or they may wish them to be somewhere outsite - even outside their project
    #         directory. We try to support both.
    #         
    #         The same is true for the CSS output file. We recommend putting it in the 
    #         MEDIA_ROOT but if there is a reason not to, we support that as well.
    #     """
    #     # if the user gives an absolute path, don't use the MEDIA_ROOT.
    #     sass_input_root = sass_input if os.path.isabs(sass_input) else settings.MEDIA_ROOT + os.path.sep + sass_input
    #     sass_output_root = css_output if os.path.isabs(css_output) else settings.MEDIA_ROOT + os.path.sep + css_output
    # 
    #     # check that the sass input file actually exists.
    #     if not os.path.exists(sass_input_root):
    #         raise SassConfigException('The input path \'%s\' seems to be invalid.\n' %sass_input_root)
    #     
    #     # make sure the output directory exists.
    #     output_path = sass_output_root.rsplit('/', 1)[0]
    #     if not os.path.exists(output_path):
    #         # try to create path
    #         try:
    #             os.mkdirs(output_path, 0644)
    #         except os.error, e:
    #             raise SassConfigException(e.message)
    #         except AttributeError, e:
    #             # we have an older version of python that doesn't support os.mkdirs - fail gracefully.
    #             raise SassConfigException('Output path does not exist - please create manually: %s\n' %output_path)
    #     print 'Processing %s' %name
        
        
    def get_file_path(self, path):
        if os.path.isabs(path):
            return path
        site_media = settings.MEDIA_ROOT
        return site_media + os.path.sep + path
        