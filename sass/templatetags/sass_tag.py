import os

from django import template
from django.conf import settings
from django.utils.http import urlquote

from sass.utils import SassUtils
from sass.models import SassModel


register = template.Library()

class SassNode(template.Node):
    def __init__(self, name):
        self.name = name

        # check to make sure the name passed into the tag is defined.
        name_is_valid = False
        for s in SassUtils.build_sass_structure():
            if s['name'] == name:
                name_is_valid = True
                self.sass_structure = s
                continue
        if not name_is_valid:
            raise template.TemplateSyntaxError('Sass name "%s" does not exist.' % self.name)
        
        
    def render(self, context):
        media_url = self.sass_structure['media_out']
        sass_obj = SassModel.objects.get(name=self.sass_structure['name'])
        css = "<link href='%s?%s' rel='stylesheet' type='text/css' />" %(media_url, sass_obj.digest)
        return css


@register.tag(name="sass")
def do_sass(parser, token):
    try:
        # get the tag and the sass resource.
        tag_name, resource = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, '%s tag requires a single argument.' %token.contents.split()[0]
    if not (resource[0] == resource[-1] and resource[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag's argument should be in quotes" % tag_name
    return SassNode(resource[1:-1])
    