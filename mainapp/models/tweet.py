from django.db import models
from django.utils import timezone


class Tweet(models.Model):
    url = models.CharField(default="https://twitter.com", null=True, blank=True)
    text = models.CharField(default="", null=True, blank=True)
    time = models.DateTimeField(default=timezone.now)
    impressions = models.IntegerField(default=0, null=True, blank=True)
    engagements = models.IntegerField(default=0, null=True, blank=True)
    engagement_rate = models.IntegerField(default=0, null=True, blank=True)
    retweets = models.IntegerField(default=0, null=True, blank=True)
    replies = models.IntegerField(default=0, null=True, blank=True)
    likes = models.IntegerField(default=0, null=True, blank=True)
    norm_score = models.IntegerField(default=0, null=True, blank=True)
    score = models.IntegerField(default=0, null=True, blank=True)
    profile_clicks = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ["-score"]
