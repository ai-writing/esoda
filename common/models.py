from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Comment(models.Model):
    user = models.ForeignKey(User)
    text = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    display = models.BooleanField(default=True)

    def __str__(self):
        return self.text
