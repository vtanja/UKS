from django.contrib import admin

from app.dashboard.models import Repository
from security.models import SiteUser

# Register your models here.
admin.site.register(Repository)
admin.site.register(SiteUser)