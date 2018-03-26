from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

from datetime import datetime


class Comment(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    display = models.BooleanField(default=False)
    session = models.CharField(max_length=40, null=True, blank=True)

    def __unicode__(self):
        return u'%s: %s' % (self.user or 'Anonymous', self.text)

    @classmethod
    def get_latest_comments(cls, limit=10):
        return list(cls.objects.filter(display=True).order_by('-date')[:limit])

class UserCorpus(models.Model):
    user = models.ForeignKey(User)
    # db = models.IntegerField(default=0)
    status = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=datetime.now)
    name = models.CharField(max_length=64)  #unique=True
    description = models.CharField(max_length=256, blank=True)
    # ispublic = models.BooleanField(default=True)

