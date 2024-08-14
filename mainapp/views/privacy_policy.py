from django.views.generic import TemplateView
from django.shortcuts import redirect


class PrivacyPolicyView(TemplateView):
    template_name = "mainapp/privacy_policy.html"
