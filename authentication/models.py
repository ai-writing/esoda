from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserWithCorpus(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	corpus_id = models.IntegerField(default=0)

def create_user_corpus(sender, instance, created, update_fields,**kwargs):
	if created:
		profile = UserWithCorpus()
		profile.user = instance
		profile.save()
	else:
		instance.userwithcorpus.save()
		 
post_save.connect(create_user_corpus, sender=User)