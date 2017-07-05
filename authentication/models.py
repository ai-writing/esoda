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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    corpus_id = models.CharField(max_length=1000,default=json.dumps([0]*1000))

    def setid(self, x):
        self.corpus_id = json.dumps(x)
    
    def getid(self):
        return json.loads(self.corpus_id)
    @staticmethod
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile(user=instance).save()

post_save.connect(UserProfile.create_user_profile, sender=User)

class TreeNode():
    def __init__(self):
        self.id = 0
        self.text = "Node 1"
        self.href = "#node-1"
        self.selectable = True
        self.state = {
             'checked': False,
        }
        self.tags = ['available']
        self.nodes = []
    def to_dict(self,checked):
        if checked==0:
            check=False
        else:
            check=True
        icon = (len(self.nodes) > 0) and 'glyphicon glyphicon-list-alt' or 'glyphicon glyphicon-user'
        return {
            'id': self.id,
            'text': self.text,
            'icon': icon,
            'tags': ['1'],
            'nodes': self.nodes,
            'state': {'checked': checked}
        }