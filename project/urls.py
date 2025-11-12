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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("", views.HomeView.as_view(), name="billing"),
    path("", views.HomeView.as_view(), name="vr"),
    path("", views.HomeView.as_view(), name="rtl"),
    path("", views.HomeView.as_view(), name="profile"),
    path("", views.HomeView.as_view(), name="password_change"),
    path("", views.HomeView.as_view(), name="logout"),
    path("dashboard/<str:user>", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard_advanced/<str:user>", views.DashboardViewAdvanced.as_view(), name="dashboard_advanced"),
    path("resize", views.ResizerView.as_view(), name="resize"),
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # accounts management
    path('tables/', views.tables, name='tables')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
