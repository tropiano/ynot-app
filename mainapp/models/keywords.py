from django.db import models
from django.utils import timezone


class Keywords(models.Model):
    user = models.CharField(default="", null=True, blank=True)
    word = models.CharField(default="https://twitter.com", null=True, blank=True)
    score = models.IntegerField(default=0, null=True, blank=True)
    norm_score = models.IntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ["-score"]
