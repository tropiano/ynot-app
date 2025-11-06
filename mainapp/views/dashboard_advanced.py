from django.views.generic import ListView
from usermodel.models import User
from django.db.models import Avg, Min, Max
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from datetime import timedelta
from django.utils import timezone
import os
from django.db.models import Sum
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
import random
import lorem
from django.shortcuts import render, redirect

class DashboardViewAdvanced(LoginRequiredMixin, ListView):
    # change the model here to the model you want to display
    template_name = "mainapp/dashboard_advanced.html"

    def get_queryset(self):
        # filter by the user first
        username = self.request.user.username
        user_dashboard = self.kwargs["user"]

        # check that the logged in user is seeing the right dashboard
        if user_dashboard != username and not self.request.user.is_superuser:
            raise PermissionDenied()

        return User.objects.filter(username=user_dashboard)

    def get_context_data(self, **kwargs):

        # filter by the user first
        # get the threads username
        username = self.request.user.username
        user_dashboard = self.kwargs["user"]

        # check that the logged in user is seeing the right dashboard
        if user_dashboard != username and not self.request.user.is_superuser:
            raise PermissionDenied()

        # get the data to enrich
        data = super().get_context_data(**kwargs)

        # add random data
        data["data"] = self.create_random_data()

        return data

    def create_random_data(self):
        # This function is just a placeholder to show how you might create random data
        # In a real application, you would replace this with actual data fetching logic

        # create a random time series
        start_date = datetime.now() - timedelta(days=30)
        data = []
        for i in range(30):
            date = start_date + timedelta(days=i)
            likes = random.randint(1, 1000)
            comments = random.randint(1, 100)
            reposts = random.randint(1, 100)
            views = random.randint(1, 100000)
            post = lorem.sentence()
            new_follow = random.randint(1, 50)
            # populate the data
            data.append(
                {
                    "date": date,
                    "likes": likes,
                    "comments": comments,
                    "reposts": reposts,
                    "views": views,
                    "avg_normscore": (likes + comments + reposts) / views,
                    "post": post,
                    "new_followers": new_follow,
                }
            )

        return data

def tables(request):
    context = {
        'parent': 'pages',
        'segment': 'tables'
    }
    return render(request, 'pages/tables.html', context)