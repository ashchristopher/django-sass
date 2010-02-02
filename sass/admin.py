from django.contrib import admin

from sass.models import SassModel

class SassModelAdmin(admin.ModelAdmin):
    pass

admin.site.register(SassModel, SassModelAdmin)