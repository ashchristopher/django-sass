import os

from django.conf import settings
from django.utils.http import urlquote


class SassUtils(object):
    
    @staticmethod
    def get_file_path(path):
        if os.path.isabs(path):
            return path
        return settings.MEDIA_ROOT + os.path.sep + path
    
    
    @staticmethod
    def get_media_url(path, media_url=settings.MEDIA_URL):
        return media_url + urlquote(path)
        
    
    @staticmethod
    def build_sass_structure():
        sass_definitions = getattr(settings, "SASS", ())

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
            sass_input_root = SassUtils.get_file_path(sass_input)
            sass_output_root = SassUtils.get_file_path(sass_output)
            sass_output_media = SassUtils.get_media_url(sass_output)
            sass_struct.append({
                'name' : sass_name,
                'input' : sass_input_root,
                'output' : sass_output_root,
                'media_out' : sass_output_media,
            })
        return sass_struct