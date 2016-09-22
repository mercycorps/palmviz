from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(CustomField)
admin.site.register(Contact)
admin.site.register(Folder)
admin.site.register(Task)
admin.site.register(CustomFieldTask)
admin.site.register(WrikeOauth2Credentials)