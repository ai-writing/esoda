from django.contrib import admin
from common.models import Comment


class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'date', 'display', 'session')

admin.site.register(Comment, CommentAdmin)
