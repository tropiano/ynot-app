from django.db import models
from django.utils import timezone


class Thread(models.Model):
    username = models.CharField(default="", null=True, blank=True)
    url = models.CharField(default="", null=True, blank=True)
    text = models.CharField(default="", null=True, blank=True)
    time = models.DateTimeField(default=timezone.now)
    short_code = models.CharField(default="", null=True, blank=True)
    threadid = models.BigIntegerField(default=0, null=True, blank=True)
    is_quote = models.BooleanField(default=False, null=True, blank=True)
    # metrics
    views = models.IntegerField(default=0, null=True, blank=True)
    engagement_rate = models.IntegerField(default=0, null=True, blank=True)
    reposts = models.IntegerField(default=0, null=True, blank=True)
    replies = models.IntegerField(default=0, null=True, blank=True)
    likes = models.IntegerField(default=0, null=True, blank=True)
    quotes = models.IntegerField(default=0, null=True, blank=True)
    # scores (calculated)
    norm_score = models.IntegerField(default=0, null=True, blank=True)
    score = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ["-score"]
