from django.views.generic import ListView
from mainapp.models.tweet import Tweet
from mainapp.models.keywords import Keywords
from django.db.models import Avg, Min, Max
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


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
