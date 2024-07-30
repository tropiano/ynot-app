from django.views.generic import ListView
from mainapp.models.tweet import Tweet
from mainapp.models.threads_profile import ThreadsProfile
from mainapp.models.thread import Thread
from mainapp.models.keywords import Keywords
from mainapp.models.keywords_threads import KeywordsThreads
from usermodel.models import User
from django.db.models import Avg, Min, Max
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from datetime import timedelta
from django.utils import timezone
import os


class DashboardView(LoginRequiredMixin, ListView):
    model = Tweet
    template_name = "mainapp/dashboard.html"

    def get_queryset(self):
        # filter by the user first
        username = self.request.user.username
        # print(username)
        user_dashboard = self.kwargs["user"]

        # check that the logged in user is seeing the right dashboard
        if user_dashboard != username and not self.request.user.is_superuser:
            raise PermissionDenied()

        # get the dashboard user tweets
        user_queryset = Tweet.objects.filter(username=user_dashboard)
        comments = self.request.GET.get("comments")

        if comments is None or comments == "yes":
            queryset = user_queryset
        # queryset = branch.objects.none()
        elif comments == "no":
            queryset = user_queryset.exclude(text__startswith="@")

        return queryset

    def get_context_data(self, **kwargs):

        # filter by the user first
        username = self.request.user.username
        # print(username)
        user_dashboard = self.kwargs["user"]

        # check that the logged in user is seeing the right dashboard
        if user_dashboard != username and not self.request.user.is_superuser:
            raise PermissionDenied()

        # get the data to enrich
        data = super().get_context_data(**kwargs)

        # get the dashboard user tweets
        user_queryset = Tweet.objects.filter(username=user_dashboard)

        stats_score = user_queryset.filter(score__gt=0).aggregate(
            Avg("score"), Min("score"), Max("score")
        )
        stats_normscore = user_queryset.aggregate(
            Avg("score"), Min("score"), Max("score")
        )
        stats_dates = user_queryset.aggregate(Min("time"), Max("time"))

        data["stats_score"] = stats_score
        data["stats_normscore"] = stats_normscore
        data["stats_dates"] = stats_dates

        # print(data["stats_dates"])
        # print(data["stats_score"])

        # get the dashboard user keywords
        user_queryset_kws = Keywords.objects.filter(username=user_dashboard)
        # get also the data about the keyword
        keywords = user_queryset_kws.order_by("-score")
        data["keywords"] = keywords

        return data


class DashboardViewThreads(LoginRequiredMixin, ListView):
    model = Thread
    template_name = "mainapp/dashboard_threads.html"

    def get_queryset(self):
        # filter by the user first
        username = self.request.user.username
        # print(username)
        user_dashboard = self.kwargs["user"]

        # check that the logged in user is seeing the right dashboard
        if user_dashboard != username and not self.request.user.is_superuser:
            raise PermissionDenied()

        # get the dashboard user posts
        user_queryset = Thread.objects.filter(username=user_dashboard)
        comments = self.request.GET.get("comments")

        if comments is None or comments == "yes":
            queryset = user_queryset
        # queryset = branch.objects.none()
        elif comments == "no":
            queryset = user_queryset.exclude(text__startswith="@")

        # print(queryset)

        return queryset

    def get_context_data(self, **kwargs):

        # filter by the user first
        # get the threads username
        threads_username = self.request.user.threads_username
        user_dashboard = self.kwargs["user"]

        # check that the logged in user is seeing the right dashboard
        if user_dashboard != threads_username and not self.request.user.is_superuser:
            raise PermissionDenied()

        # get the data to enrich
        data = super().get_context_data(**kwargs)

        # get the user threads profile
        user_queryset = ThreadsProfile.objects.filter(username=user_dashboard)

        followers = user_queryset.first().followers
        bio = user_queryset.first().biography
        likes = user_queryset.first().likes
        replies = user_queryset.first().replies
        reposts = user_queryset.first().reposts
        quotes = user_queryset.first().quotes

        # last_update = user_queryset.first().profile_last_update

        data["followers"] = followers
        data["bio"] = bio
        data["likes"] = likes
        data["replies"] = replies
        data["reposts_quotes"] = reposts + quotes

        # get the dashboard user keywords
        user_queryset_kws = KeywordsThreads.objects.filter(username=user_dashboard)
        # get also the data about the keyword
        keywords = user_queryset_kws.order_by("-score")
        data["keywords"] = keywords

        if User.objects.filter(threads_username=user_dashboard).first().is_free_trial:
            data["trial_expired"] = False
        else:
            data["trial_expired"] = True

        data["trial_exp_date"] = (
            User.objects.filter(threads_username=user_dashboard).first().date_joined
        ) + timedelta(days=int(os.environ["FREE_TRIAL_DAYS"]))

        # get the user last update
        data["profile_last_update"] = (
            User.objects.filter(threads_username=user_dashboard)
            .first()
            .profile_last_update
        )

        threads_update_date = (
            User.objects.filter(threads_username=user_dashboard)
            .first()
            .threads_last_update
        )

        if timezone.now() > threads_update_date + timedelta(days=1):
            data["old_update"] = True

        return data


class DashboardViewTest(ListView):
    model = Tweet
    template_name = "mainapp/example_dashboard.html"
    username = "tropianhs"

    def get_queryset(self):
        # get the dashboard user tweets
        user_queryset = Tweet.objects.filter(username=self.username)
        comments = self.request.GET.get("comments")
        # print(self.username)
        if comments is None or comments == "yes":
            queryset = user_queryset
        # queryset = branch.objects.none()
        elif comments == "no":
            queryset = user_queryset.exclude(text__startswith="@")

        return queryset

    def get_context_data(self, **kwargs):

        # get the dashboard user tweets
        user_queryset = Tweet.objects.filter(username=self.username)
        # get the dashboard user keywords
        user_queryset_kws = Keywords.objects.filter(username=self.username)

        data = super().get_context_data(**kwargs)
        stats_score = user_queryset.filter(score__gt=0).aggregate(
            Avg("score"), Min("score"), Max("score")
        )
        stats_normscore = user_queryset.aggregate(
            Avg("score"), Min("score"), Max("score")
        )
        stats_dates = user_queryset.aggregate(Min("time"), Max("time"))

        data["stats_score"] = stats_score
        data["stats_normscore"] = stats_normscore
        data["stats_dates"] = stats_dates

        # get also the data about the keyword
        keywords = user_queryset_kws.order_by("-score")
        data["keywords"] = keywords

        return data
