from django.views.generic import ListView
from usermodel.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from datetime import timedelta
from django.utils import timezone
import os
from datetime import datetime
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import uuid
import time
from django.core.cache import cache
from django.http import HttpResponse
from mainapp.models import Upload


# if more than limit, return empty response
LIMIT = int(os.environ.get("UPLOAD_LIMIT_PER_DAY", "10"))

class DashboardView(LoginRequiredMixin, ListView):
    # change the model here to the model you want to display
    template_name = "mainapp/dashboard.html"

    def get(self, request, *args, **kwargs):
        # permission check (same logic as other methods)
        username = request.user.username
        user_dashboard = self.kwargs.get("user")
        if user_dashboard != username and not request.user.is_superuser:
            raise PermissionDenied()

        resized_dir = os.path.join("resized", username)
        images = []
        
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context["upload_limit_reached"] = False

        # rate-limit uploads per IP: if >= X uploads in last 24 hours, add flag to context
        client_ip = self._get_client_ip(request) or "unknown"
        db_count = self._count_uploads_last_24h(client_ip)
        if db_count >= LIMIT:
            # reached limit -> add flag to context
            context["upload_limit_reached"] = True
        
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
                    saved_date = datetime(mtime).date().isoformat()
                except Exception:
                    saved_time = mtime.isoformat() if hasattr(mtime, "isoformat") else str(mtime)
                    saved_date = mtime.date().isoformat() if hasattr(mtime, "date") else None
            except Exception:
                saved_time = None
                saved_date = None

            images.append({"name": fname, "path": rel_path, "url": url, "saved_time": saved_time, "saved_date": saved_date})

        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"images": images})

        # For normal GET, include images in the template context
        context["resized_images"] = sorted(images, key=lambda x: x["saved_time"] or "", reverse=True)
        print([x['saved_date'] for x in context["resized_images"]])

        return self.render_to_response(context)
    
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

        # rate-limit uploads per IP: if >= 10 uploads in last 24 hours, return empty response
        client_ip = self._get_client_ip(request) or "unknown"

        # count number of files being uploaded in this request (support images[] or image)
        files_count = len(request.FILES.getlist("images"))
        if files_count == 0 and "image" in request.FILES:
            files_count = 1

        db_count = self._count_uploads_last_24h(client_ip)

        if db_count >= LIMIT:
            # reached limit -> return empty 204 No Content response
            return HttpResponse(status=204)

        # gather uploaded files (support both single and multiple inputs)
        files = request.FILES.getlist("images")
        # print("FILES:", request.FILES)
        if not files and "image" in request.FILES:
            files = [request.FILES["image"]]

        saved_paths = self._save_uploaded_images(files, user_dashboard)

        # add a virtual 5 second delay to simulate processing time
        time.sleep(5)

        now = timezone.now()

        # record uploads with IP and timestamp
        for _ in saved_paths:
            # best-effort create with common field names
            create_kwargs = {"ip": client_ip, "upload_date": now}
            Upload.objects.create(**create_kwargs)

        # respond appropriately for AJAX vs normal form submit
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"saved": saved_paths})
        else:
            return HttpResponseRedirect(request.path)

    def _get_client_ip(self, req):
            xff = req.META.get("HTTP_X_FORWARDED_FOR")
            if xff:
                return xff.split(",")[0].strip()
            return req.META.get("REMOTE_ADDR")
    
    def _count_uploads_last_24h(self, ip):
        # count recent uploads from the uploads model (past 24 hours)
        db_count = 0
        if Upload is not None:
            # count uploads from midnight today (timezone-aware)
            now = timezone.localtime(timezone.now())
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            try:
                db_count = Upload.objects.filter(upload_date__gte=start_of_day, ip=ip).count()
            except Exception:
                    db_count = 0
        
        return db_count
    
    def _save_uploaded_images(self, files, username):
        """
        Helper to persist uploaded files using Django's default storage.
        Returns a list of saved relative paths.
        """

        saved = []
        resized = []
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
            resized.append(resized_path)

        return resized


    def get_queryset(self):
        # filter by the user first
        username = self.request.user.username
        user_dashboard = self.kwargs["user"]

        # check that the logged in user is seeing the right dashboard
        if user_dashboard != username and not self.request.user.is_superuser:
            raise PermissionDenied()

        return User.objects.filter(username=user_dashboard)