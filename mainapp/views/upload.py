from mainapp.forms.upload import DocumentForm
from django.shortcuts import render
from django.shortcuts import redirect


def model_form_upload(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("success")

    else:
        form = DocumentForm()

    return render(request, "mainapp/upload.html", {"form": form})


def success(request):

    return render(request, "mainapp/upload_success.html")
