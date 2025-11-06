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
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
import time

class DashboardView(LoginRequiredMixin, ListView):
    # change the model here to the model you want to display
    template_name = "mainapp/dashboard.html"

    def post(self, request, *args, **kwargs):
        """
        Handle form submissions that include image files.
        Accepts files under the field name 'images' (multiple) or 'image' (single).
        Saves files to the default storage under uploads/<username>/ and returns
        JSON for AJAX requests or redirects back to the same page for normal form posts.
        """
        # permission check (same logic as other methods)
        username = request.user.username
        user_dashboard = self.kwargs.get("user")
        if user_dashboard != username and not request.user.is_superuser:
            raise PermissionDenied()

        # gather uploaded files (support both single and multiple inputs)
        files = request.FILES.getlist("images")
        # print("FILES:", request.FILES)
        if not files and "image" in request.FILES:
            files = [request.FILES["image"]]

        
        saved_paths = self._save_uploaded_images(files, user_dashboard)

        # add a virtual 5 second delay to simulate processing time
        time.sleep(5)

        # respond appropriately for AJAX vs normal form submit
        if request.headers.get("x-requested-with") == "XMLHttpRequest":

            return JsonResponse({"saved": saved_paths})
        else:

            return HttpResponseRedirect(request.path)


    def _save_uploaded_images(self, files, username):
        """
        Helper to persist uploaded files using Django's default storage.
        Returns a list of saved relative paths.
        """

        saved = []
        if not files:
            return saved

        media_subdir = os.path.join("uploads", username)
        media_resized_subdir = os.path.join("resized", username)

        for f in files:
            ext = os.path.splitext(f.name)[1]
            filename = f"{uuid.uuid4().hex}{ext}"
            rel_path = os.path.join(media_subdir, filename)
            rel_resized_path = os.path.join(media_resized_subdir, filename)
            # read file content once and save via storage backend
            data = f.read()
            path = default_storage.save(rel_path, ContentFile(data))
            saved.append(path)
            # Here you would add your image resizing logic and save to rel_resized_path
            # (use the same in-memory data or replace `data` with resized bytes)
            resized_path = default_storage.save(rel_resized_path, ContentFile(data))
            saved.append(resized_path)

        return saved
    
    def get(self, request, *args, **kwargs):
        # permission check (same logic as other methods)
        username = request.user.username
        user_dashboard = self.kwargs.get("user")
        if user_dashboard != username and not request.user.is_superuser:
            raise PermissionDenied()

        resized_dir = os.path.join("resized", username)
        images = []

        try:
            dirs, files = default_storage.listdir(resized_dir)
        except Exception:
            files = []

        for fname in files:
            rel_path = os.path.join(resized_dir, fname)
            try:
                url = default_storage.url(rel_path)
            except Exception:
                url = rel_path
            try:
                mtime = default_storage.get_modified_time(rel_path)
                try:
                    saved_time = datetime(mtime).isoformat()
                except Exception:
                    saved_time = mtime.isoformat() if hasattr(mtime, "isoformat") else str(mtime)
            except Exception:
                saved_time = None

            images.append({"name": fname, "path": rel_path, "url": url, "saved_time": saved_time})

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"images": images})

        # For normal GET, include images in the template context
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context["resized_images"] = sorted(images, key=lambda x: x["saved_time"] or "", reverse=True)

        return self.render_to_response(context)

    def get_queryset(self):
        # filter by the user first
        username = self.request.user.username
        user_dashboard = self.kwargs["user"]

        # check that the logged in user is seeing the right dashboard
        if user_dashboard != username and not self.request.user.is_superuser:
            raise PermissionDenied()

        return User.objects.filter(username=user_dashboard)