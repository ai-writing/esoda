from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Corpus(models.Model):
	name = models.CharField('name', max_length=30)
	c_id = models.IntegerField('c_id')
	parent = models.ForeignKey('self', blank=True, null=True, related_name='children', verbose_name='parent')
	deep_level = models.IntegerField('depth', default=0)
	def __str__(self):
		return self.name

class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	corpus_id = models.ForeignKey(Corpus, related_name='peoples',null=True, verbose_name='domain',default=None)

	@staticmethod
	def create_user_profile(sender, instance, created, **kwargs):
		if created:
			UserProfile(user=instance).save()
		else:
			instance.userprofile.corpus_id = Corpus.objects.get(c_id=0)
			instance.userprofile.save()

post_save.connect(UserProfile.create_user_profile, sender=User)

class TreeNode():
	def __init__(self):
		self.id = 0
		self.text = "Node 1"
		self.href = "#node-1"
		self.selectable = True
		self.state = {
			 'checked': True,
			 'disabled': True,
			 'expanded': True,
			 'selected': True,
		}
		self.tags = ['available']
		self.nodes = []
	def to_dict(self):
		icon = (len(self.nodes) > 0) and 'glyphicon glyphicon-list-alt' or 'glyphicon glyphicon-user'
		return {
			'id': self.id,
			'text': self.text,
			'icon': icon,
			'href': self.href,
			'tags': ['1'],
			'nodes': self.nodes,
		}