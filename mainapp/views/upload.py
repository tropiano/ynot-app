from mainapp.forms.upload import DocumentForm, FileFieldForm

# from mainapp.scripts.analyze_user_tweets import score, write_db
# import pandas as pd
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from usermodel.models import User
from mainapp.models.upload import Document


def model_form_upload(request):
    user_name = request.user.username

    if not user_name:
        return redirect("login")

    if request.method == "POST":
        form = FileFieldForm(request.POST, request.FILES)
        files = request.FILES.getlist("file_field")
        # files = form.cleaned_data["file_field"]
        file_insts = []
        if form.is_valid():
            for file in files:
                file_instance = Document(document=file)
                file_instance.save()
                file_insts.append(file_instance.document.url)
                # file_obj = form.save(commit=False)
                # file_obj.save()
            #  print(file_obj.document.url)
            # execute task to populate DB
            init_db(request, file_insts)
            return redirect("success")

    else:
        form = FileFieldForm()

    return render(request, "mainapp/upload.html", {"form": form})


def success(request):

    return render(request, "mainapp/upload_success.html")


def init_db(request, files):

    # disable for now
    return
    # print(os.environ["MEDIA_ROOT"])
    # print(file_path)
    df_list = []
    for file in files:
        file_path = "/".join(file.split("/")[2:])
        tweet_file = f"{settings.MEDIA_ROOT}/{file_path}"
        # user_name = tweet_file.split("/")[-1].split("_")[3]
        user_name = request.user.username
        df_list.append(pd.read_csv(tweet_file))
    # concatenate all dataframes
    df_full = pd.concat(df_list)
    # drop the duplicates (just in case)
    df_full = df_full.drop_duplicates(subset=["Tweet permalink"])
    # apply the function that calculates the score
    df_full["score"] = df_full.apply(lambda x: score(x)[0], axis=1)
    df_full["norm_score"] = df_full.apply(lambda x: score(x)[1], axis=1)
    # write results to the DB
    write_db(df_full, user_name)
