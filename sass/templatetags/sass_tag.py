from django import template
from sass.models import SassModel
from sass.management.commands import sassify


register = template.Library()

class SassNode(template.Node):
    def __init__(self, name):
        try:
            command = sassify.Command()
            command.process_sass(name=name)
            self.model = SassModel.objects.get(name=name)
        except SassModel.DoesNotExist:
            raise template.TemplateSyntaxError('Sass name "%s" does not exist.' % self.name)


    def render(self, context):
        media_url = self.model.css_media_path()
        css = "<link href='%s?%s' rel='stylesheet' type='text/css' />" %(media_url, self.model.source_modified_time)
        return css


@register.tag(name="sass")
def do_sass(parser, token):
    try:
        # get the tag and the sass resource.
        tag_name, resource = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%s tag requires a single argument.' %token.contents.split()[0])
    if not (resource[0] == resource[-1] and resource[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's argument should be in quotes" % tag_name)
    return SassNode(resource[1:-1])
