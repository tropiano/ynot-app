# create a custom adapter
from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url


class LoginRedirectAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        username = request.user.username
        url = f"/dashboard/{username}"
        return resolve_url(url)
