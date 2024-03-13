"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from mainapp import views
from mainapp.views import upload
from mainapp.views import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView


urlpatterns = [
    path("", views.WelcomeToSpeedPyView.as_view(), name="home"),
    path("dashboard/<str:user>", views.DashboardView.as_view(), name="dashboard"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # accounts management
    # only allow twitter social login/signup
    path("accounts/login/", RedirectView.as_view(url="/accounts/twitter/login/")),
    path("accounts/signup/", RedirectView.as_view(url="/accounts/twitter/signup/")),
    path("accounts/logout/", RedirectView.as_view(url="/accounts/twitter/logout/")),
    path("upload/", upload.model_form_upload, name="upload"),  # upload form
    path("success/", upload.success, name="success"),  # upload form success
    path(
        "redirect/", redirect.CurrentUserProfileRedirectView.as_view(), name="redirect"
    ),  # redirect after login
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
