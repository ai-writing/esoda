from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from models import UserWithCorpus

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class UserWithCorpusInline(admin.StackedInline):
    model = UserWithCorpus
    can_delete = False
    verbose_name_plural = 'userwithcorpus'

# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (UserWithCorpusInline, )

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)