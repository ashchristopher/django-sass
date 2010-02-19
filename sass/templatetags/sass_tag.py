import os

from django import template
from django.conf import settings
from django.utils.http import urlquote


register = template.Library()

class SassNode(template.Node):
    def __init__(self, name):
        self.name = name
    
    def render(self, context):
        css = "<link href='' rel='stylesheet' type='text/css' />"
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
    