from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


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
