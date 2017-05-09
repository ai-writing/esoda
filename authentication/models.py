from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    corpus_id = models.IntegerField(default=0)

    @staticmethod
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile(user=instance).save()
        else:
            instance.userprofile.corpus_id = 9
            instance.userprofile.save()

post_save.connect(UserProfile.create_user_profile, sender=User)
