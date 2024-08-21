from django.db import models


class KeywordsThreads(models.Model):
    # same keyword/topic model but for threads posts
    username = models.CharField(default="", null=True, blank=True)
    word = models.CharField(default="https://twitter.com", null=True, blank=True)
    score = models.FloatField(default=0, null=True, blank=True)
    norm_score = models.FloatField(default=0, null=True, blank=True)

    class Meta:
        ordering = ["-score"]
