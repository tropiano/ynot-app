from django.db import models


class ThreadsProfile(models.Model):
    threads_id = models.BigIntegerField(default=0, null=True, blank=True)
    username = models.CharField(default="", null=True, blank=False, unique=True)
    name = models.CharField(default="", null=True, blank=False, unique=False)
    biography = models.CharField(default="", null=True, blank=True)
    profile_pic_url = models.CharField(default="", null=True, blank=True)
    followers = models.IntegerField(default=0, null=True, blank=True)
    likes = models.IntegerField(default=0, null=True, blank=True)
    replies = models.IntegerField(default=0, null=True, blank=True)
    reposts = models.IntegerField(default=0, null=True, blank=True)
    quotes = models.IntegerField(default=0, null=True, blank=True)
