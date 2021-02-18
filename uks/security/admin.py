from django.contrib import admin

from apps.repository.models import Repository
from security.models import SiteUser
from apps.label.models import Label
from apps.tag.models import Tag
# Register your models here.

admin.site.register(Repository)
admin.site.register(SiteUser)
admin.site.register(Label)
admin.site.register(Tag)
