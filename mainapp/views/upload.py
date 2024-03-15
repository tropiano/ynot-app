from mainapp.forms.upload import DocumentForm
from mainapp.tasks.analyze_user_tweets import score, write_db
from django.shortcuts import render
from django.shortcuts import redirect
import pandas as pd
import os
from django.conf import settings


def model_form_upload(request):
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = form.save(commit=False)
            file_obj.save()
            #  print(file_obj.document.url)
            # execute task to populate DB
            init_db(request, file_obj.document.url)
            return redirect("success")

    else:
        form = DocumentForm()

    return render(request, "mainapp/upload.html", {"form": form})


def success(request):

    return render(request, "mainapp/upload_success.html")


def init_db(request, file_path):

    print(os.environ["MEDIA_ROOT"])
    print(file_path)
    tweet_file = f"{os.environ['MEDIA_ROOT']}{file_path}"
    # user_name = tweet_file.split("/")[-1].split("_")[3]
    user_name = request.user.username
    df_full = pd.read_csv(tweet_file)
    # apply the function that calculates the score
    df_full["score"] = df_full.apply(lambda x: score(x)[0], axis=1)
    df_full["norm_score"] = df_full.apply(lambda x: score(x)[1], axis=1)
    # write results to the DB
    write_db(df_full, user_name)
