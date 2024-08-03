from django.contrib import admin
from mainapp.models import ThreadsProfile


class ThreadsProfileAdmin(admin.ModelAdmin):
    list_display = ("username", "threads_id", "profile_pic_url")


admin.site.register(ThreadsProfile, ThreadsProfileAdmin)
