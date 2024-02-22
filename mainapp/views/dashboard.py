from django.views.generic import TemplateView
from django.views.generic import ListView
from mainapp.models.tweet import Tweet
from mainapp.models.keywords import Keywords
from django.db.models import Avg, Min, Max


class DashboardView(ListView):
    model = Tweet
    template_name = "mainapp/dashboard.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        stats_score = Tweet.objects.aggregate(Avg("score"), Min("score"), Max("score"))
        stats_normscore = Tweet.objects.aggregate(
            Avg("score"), Min("score"), Max("score")
        )

        data["stats_score"] = stats_score
        data["stats_normscore"] = stats_normscore

        # get also the data about the keyword
        keywords = Keywords.objects.order_by("-score")
        data["keywords"] = keywords
        
        return data
