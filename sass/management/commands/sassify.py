import sys, os
from optparse import make_option
from commands import getstatusoutput

from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.management.color  import no_style
from django.utils.http import urlquote

from sass.models import SASS_ROOT, SassModel
from sass.utils import update_needed
from sass.exceptions import SassConfigException, SassConfigurationError, SassCommandArgumentError, SassGenerationError, SassException


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

        self.sass_style = getattr(settings, "SASS_STYLE", 'nested')


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
                    'input_file' : os.path.join(SASS_ROOT, sass_def['details']['input']),
                    'output_file' : os.path.join(SASS_ROOT, sass_def['details']['output']),
                    # 'media_output' : settings.MEDIA_URL + urlquote(sass_def['details']['output']),
                }
                definitions.append(sd)
            except KeyError:
                raise SassConfigurationError("Improperly defined SASS definition.")
        return definitions


    def process_sass(self, name=None, force=False):
        if force:
            print "Forcing sass to run on all files."
        sass_definitions = self.get_sass_definitions()
        for sass_def in sass_definitions:
            if not name or name == sass_def['name']:
                self.generate_css_file(force=force, **sass_def)



    def generate_css_file(self, force, name, input_file, output_file, **kwargs):
        # check that the sass input file actually exists.
        if not os.path.exists(input_file):
            raise SassConfigException('The input \'%s\' does not exist.\n' %input_file)
        output_path = output_file.rsplit('/', 1)[0]
        if not os.path.exists(output_path):
            # try to create path
            try:
                os.mkdirs(output_path, 0644)
            except os.error, e:
                raise SassConfigException(e.message)
            except AttributeError, e:
                # we have an older version of python that doesn't support os.mkdirs - fail gracefully.
                raise SassConfigException('Output path does not exist - please create manually: %s\n' %output_path)

        try:
            sass_obj = SassModel.objects.get(name=name)
            was_created = False
        except SassModel.DoesNotExist:
            sass_obj = SassModel(name=name)
            was_created = True

        sass_obj.sass_path = input_file
        sass_obj.css_path = output_file

        needs_update = was_created or force or update_needed(sass_obj)
        if needs_update:
            sass_dict = { 'bin' : self.bin, 'sass_style' : self.sass_style, 'input' : input_file, 'output' : output_file }
            cmd = "%(bin)s -t %(sass_style)s -C %(input)s > %(output)s" %sass_dict
            (status, output) = getstatusoutput(cmd)
            if not status == 0:
                raise SassException(output)
            sass_obj.save()


    def clean(self):
        for s in SassModel.objects.all():
            try:
                print "Removing css: %s" % s.css_path
                os.remove(s.css_path)
                s.delete()
            except OSError, e:
                raise e


    def list(self):
        """
        We check to see if the Sass outlined in the SASS setting are different from what the databse
        has stored. We only care about listing those files that are in the SASS setting. Ignore the
        settings in the DB if the files/settings have been removed.
        """
        # process the Sass information in the settings.
        sass_definitions = self.get_sass_definitions()
        for sass_def in sass_definitions:
            print "[%s]" % sass_def['name']
            try:
                sass_obj = SassModel.objects.get(name=sass_def['name'])
                sass_obj.sass_path = sass_def['input_file']
                sass_obj.css_path = sass_def['output_file']
                was_created = False
            except SassModel.DoesNotExist:
                sass_obj = SassModel(name=sass_def['name'])
                was_created = True
            needs_update = was_created or update_needed(sass_obj)
            if needs_update:
                print "\tChanges detected."
