from django.db import models

class Upload(models.Model):
    ip = models.GenericIPAddressField(protocol='both', unpack_ipv4=True)
    upload_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-upload_date",)
        verbose_name = "Upload"
        verbose_name_plural = "Uploads"

    def __str__(self):
        return f"{self.ip} @ {self.upload_date.isoformat()}"