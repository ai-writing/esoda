from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import json

# class Corpus(models.Model):
#     name = models.CharField('name', max_length=30)
#     c_id = models.IntegerField('c_id')
#     parent = models.ForeignKey('self', blank=True, null=True, related_name='children', verbose_name='parent')
#     deep_level = models.IntegerField('depth', default=0)
#     def __str__(self):
#         return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    corpus_id = models.CharField(max_length=10000, default=json.dumps([0]*2000, separators=(',', ':')))

    def setid(self, x):
        self.corpus_id = json.dumps(x, separators=(',', ':'))
    
    def getid(self):
        try:
            ids = json.loads(self.corpus_id)
        except ValueError, e:
            ids = [0]*2000
            self.corpus_id = json.dumps(ids, separators=(',', ':'))
            self.save()
        return ids

    @staticmethod
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile(user=instance).save()

post_save.connect(UserProfile.create_user_profile, sender=User)

