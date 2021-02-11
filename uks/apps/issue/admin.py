from django.contrib import admin
from .models import Issue, IssueChange

# Register your models here.
admin.site.register(Issue)
admin.site.register(IssueChange)
