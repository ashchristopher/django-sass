import sys, os, hashlib
from optparse import make_option
from commands import getstatusoutput

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management.color  import no_style

from sass.models import SassModel
from sass.utils import SassUtils

class SassConfigException(Exception):
    pass

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
    
    
    def handle(self, *args, **kwargs):
        self.bin = getattr(settings, "SASS_BIN", None)
        if not self.bin:
            sys.stderr.write(self.style.ERROR('SASS_BIN is not defined in settings.py file.\n'))
            return
        # test that binary defined exists
        if not os.path.exists(self.bin):
            sys.stderr.write(self.style.ERROR('Sass binary defined by SASS_BIN does not exist: %s\n' %bin))
            return    
        
        # make sure the Sass style given is valid.
        self.sass_style = kwargs.get('sass_style')
        if self.sass_style not in ('nested', 'compact', 'compressed', 'expanded'):
            sys.stderr.write(self.style.ERROR("Invalid sass style argument: %s\n") %self.sass_style)
            return
        
        if kwargs.get('list_sass'):
            self.list()
        elif kwargs.get('clean'):
            self.clean()
        else:
            self.process_sass(force=kwargs.get('force_sass'))

         
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
            sass_file_digest = self.md5_file(sass_instance['input'])
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


    def process_sass(self, force=False):
        if force:
            print "\nForcing sass to run on all files.\n"
        sass_struct = SassUtils.build_sass_structure()
        for sass_info in sass_struct:
            try:
                self.process_sass_file(
                    sass_info.get('name'),
                    sass_info.get('input'),
                    sass_info.get('output'),
                    force
                )
            except SassConfigException, e:
                sys.stderr.write(self.style.ERROR(e.message))
            
            
    def process_sass_file(self, name, input_file, output_file, force):
        print "[%s]" %name
        # check that the sass input file actually exists.
        if not os.path.exists(input_file):
            raise SassConfigException('The input path \'%s\' seems to be invalid.\n' %input_file)
        # make sure the output directory exists.
        output_path = output_file.rsplit('/', 1)[0]
        self._prepare_dir(output_path)
        
        sass_obj, was_created = SassModel.objects.get_or_create(name=name)
        input_digest = self.md5_file(input_file)
        
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
        
        
    def md5_file(self, filename):
        try:
            md5 = hashlib.md5()
            fd = open(filename,"rb")
            content = fd.readlines()
            fd.close()
            for line in content:
                md5.update(line)
            return md5.hexdigest()
        except IOError, e:
            raise SassConfigException(e.message)
        