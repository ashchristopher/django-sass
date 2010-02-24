import sys, os
from optparse import make_option
from commands import getstatusoutput

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management.color  import no_style
from django.utils.http import urlquote

from sass.models import SassModel
from sass.utils import SassUtils
from sass.exceptions import SassConfigException, SassConfigurationError, SassCommandArgumentError


class Command(BaseCommand):
    """
        The user may whish to keep their sass files in their MEDIA_ROOT directory,
        or they may wish them to be somewhere outsite - even outside their project
        directory. We try to support both.
        
        The same is true for the CSS output file. We recommend putting it in the 
        MEDIA_ROOT but if there is a reason not to, we support that as well.
    """
    
    requires_model_validation = False
    can_import_settings = True
    style = no_style()
    
    option_list = BaseCommand.option_list + ( 
        make_option('--style', '-t', dest='sass_style', default='nested', help='Sass output style. Can be nested (default), compact, compressed, or expanded.'),
        make_option('--list', '-l', action='store_true', dest='list_sass' , default=None, help='Display information about the status of your sass files.'),
        make_option('--force', '-f', action='store_true', dest='force_sass', default=False, help='Force sass to run.'),
        make_option('--clean', '-c', action='store_true', dest='clean', default=False, help='Remove all the generated CSS files.'),
    )
    help = 'Converts Sass files into CSS.'
    
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)
        self.bin = getattr(settings, "SASS_BIN", None)
        if not self.bin:
            raise SassConfigurationError('SASS_BIN is not defined in settings.py file.')
        # test that the binary actually exists.
        if not os.path.exists(self.bin):
            raise SassConfigurationError('Sass binary defined by SASS_BIN does not exist: %s' % self.bin)
    
    
    def handle(self, *args, **kwargs):
        # make sure the Sass style given is valid.
        self.sass_style = kwargs.get('sass_style')
        if self.sass_style not in ('nested', 'compact', 'compressed', 'expanded'):
            raise SassCommandArgumentError("Invalid sass style argument: %s" % self.sass_style)
        
        force = kwargs.get('force_sass')
        list_sass = kwargs.get('list_sass')
        clean = kwargs.get('clean')
        
        # we process the args in the order of least importance to hopefully stop
        # any unwanted permanent behavior.
        
        if list_sass:
            self.list()
        elif clean:
            self.clean()
        else:
            self.process_sass(force=kwargs.get('force_sass'))

    def get_sass_definitions(self):
        definitions = []
        for sass_def in getattr(settings, "SASS", ()):
            try:
                sd = {
                    'name' : sass_def['name'],
                    'input' : os.path.join(settings.MEDIA_ROOT, sass_def['details']['input']),
                    'output' : os.path.join(settings.MEDIA_ROOT, sass_def['details']['output']),
                    'media_output' : settings.MEDIA_URL + urlquote(sass_def['details']['output']),
                }
                definitions.append(sd)
            except KeyError:
                raise SassConfigurationError("Improperly defined SASS definition.")
        return definitions
        

    def process_sass(self, force=False):
        if force:
            print "Forcing sass to run on all files."
        sass_definitions = self.get_sass_definitions()
        for sass_def in sass_definitions:
            print sass_def


    def generate_css_file(self, name, input, output):
        pass


    def _remove_file(self, path_to_file):
        try:
            os.remove(path_to_file)
            return "Removed %s" % path_to_file
        except OSError, e:
            # there is no recovery for these errors - just display to the user.
            return e.strerror

        
    def _prepare_dir(self, output_path):
        if not os.path.exists(output_path):
            # try to create path
            try:
                os.mkdirs(output_path, 0644)
            except os.error, e:
                raise SassConfigException(e.message)
            except AttributeError, e:
                # we have an older version of python that doesn't support os.mkdirs - fail gracefully.
                raise SassConfigException('Output path does not exist - please create manually: %s\n' %output_path)
    
    
    def _list_sass(self, sass_instance):
        print "[%s]" % sass_instance['name']
        # get the digest we have stored and compare to the hash we have on disk.
        try:
            # hash from db.
            sass_obj = SassModel.objects.get(name=sass_instance['name'])
            sass_digest = sass_obj.digest
        except (SassModel.DoesNotExist):
            sass_digest = None
            
        try:
            # digest from disk.
            sass_file_digest = SassUtils.md5_file(sass_instance['input'])
        except SassConfigException, e:
            # not really sure what we want to do with this exception.
            raise e
        
        # check that a CSS file exists - if not, report to the user.
        if not os.path.exists(sass_instance['output']):
            print "\tInput: %s" % sass_instance['input']
            print "\tOutput: %s" % sass_instance['output']
            print "\n\tCSS needs to be generated.\n"
        elif sass_file_digest == sass_digest:
            print "\tInput: %s" % sass_instance['input']
            print "\tOutput: %s" % sass_instance['output']
            
            print "\n\tUp to date.\n"
        else:
            # give out information about the changes.
            print "\tUpdate required\n\t---------------"
            print "\t%s" % sass_instance['input']
            print "\tPrevious: %s" % sass_digest
            print "\tCurrent:  %s" % sass_file_digest

    
    def clean(self):
        sass_struct = SassUtils.build_sass_structure()
        for sd in sass_struct:
            print "[%s]" % sd['name']
            msg = self._remove_file(path_to_file=sd['output'])
            print "\t%s" % msg
    
    
    def list(self):
        """
        We check to see if the Sass outlined in the SASS setting are different from what the databse
        has stored. We only care about listing those files that are in the SASS setting. Ignore the 
        settings in the DB if the files have been removed.
        
        Output in the format only if there are differences.:
        
            <name> <old_hash> <current_hash>
            
            If there are no changes, output at the end of the script that there were no changes.
        """
        # process the Sass information in the settings.
        sass_struct = SassUtils.build_sass_structure()
        for si in sass_struct:
            self._list_sass(sass_instance=si)
            
            
    def process_sass_file(self, name, input_file, output_file, force):
        print "[%s]" %name
        # check that the sass input file actually exists.
        if not os.path.exists(input_file):
            raise SassConfigException('The input path \'%s\' seems to be invalid.\n' %input_file)
        # make sure the output directory exists.
        output_path = output_file.rsplit('/', 1)[0]
        self._prepare_dir(output_path)
        
        sass_obj, was_created = SassModel.objects.get_or_create(name=name)
        input_digest = SassUtils.md5_file(input_file)
        
        if not input_digest == sass_obj.digest or not os.path.exists(output_file) or force:
            sass_dict = { 'bin' : self.bin, 'sass_style' : self.sass_style, 'input' : input_file, 'output' : output_file }
            cmd = "%(bin)s -t %(sass_style)s -C %(input)s > %(output)s" %sass_dict
            (status, output) = getstatusoutput(cmd)
            if status:
                raise SassConfException(output)
            # if we successfully generate the file, save the model to the DB.    
            sass_obj.name = name
            sass_obj.sass_path = input_file
            sass_obj.css_path = output_file
            sass_obj.digest = input_digest
            sass_obj.save()
            print "\tGenerated new CSS file: %s" %sass_obj.css_path
        else:
            print "\tAlready up to date."
        