from mainapp.forms.upload import DocumentForm, FileFieldForm
from mainapp.tasks.analyze_user_tweets import score, write_db
from django.shortcuts import render
from django.shortcuts import redirect
import pandas as pd
from django.conf import settings
from usermodel.models import User
from mainapp.models.threads_profile import ThreadsProfile
import requests as r
import os


def authorize(request):

    user_name = request.user.username
    print(user_name)

    if not user_name:
        return redirect("login")

    # get the short access token
    # get the long access token and save
    current_path = request.get_full_path()
    print(current_path)
    return_code = current_path.split("?code=")[1]
    auth_code = return_code.split("#_")[0]
    print(auth_code)
    save_long_token(auth_code, user_name)
    save_user_info(user_name)

    return redirect("dashboard_threads", user=user_name)


def save_long_token(auth_code, user_name):

    # define the parameters
    get_token_url = "https://graph.threads.net/oauth/access_token"
    threads_app_secret = os.getenv("THREADS_APP_SECRET")
    threads_app_id = os.getenv("THREADS_APP_ID")
    threads_redirect_uri = os.getenv("THREADS_REDIRECT_URI")

    data = {
        "client_id": threads_app_id,
        "client_secret": threads_app_secret,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": threads_redirect_uri,
    }

    response = r.post(get_token_url, data=data)

    # get the short token and user id
    short_token = response.json()["access_token"]

    # get long lived token
    long_token_url = f"https://graph.threads.net/access_token?grant_type=th_exchange_token&client_secret={threads_app_secret}&access_token={short_token}"
    response = r.get(long_token_url)
    long_token = response.json()["access_token"]

    # save the long lived token in the User model
    # field is encrypted
    User.objects.filter(username=user_name).update(threads_token=long_token)

    # mark the user as threads user
    User.objects.filter(username=user_name).update(has_threads=True)


def save_user_info(user_name):

    # get the token to make all requests
    long_token = User.objects.filter(username=user_name).first().threads_token

    # get the threads username and bio
    url_user_profile = f"https://graph.threads.net/v1.0/me?fields=id,username,threads_profile_picture_url,threads_biography&access_token={long_token}"
    response = r.get(url_user_profile)
    threads_username = response.json()["username"]
    threads_bio = response.json()["threads_biography"]
    threads_profile_pic_url = response.json()["threads_profile_picture_url"]
    threads_id = response.json()["id"]

    # update threads username in main user model
    User.objects.filter(username=user_name).update(threads_username=threads_username)

    # create record threads_profile
    if not ThreadsProfile.objects.filter(username=threads_username):
        user_threads_profile = ThreadsProfile(
            username=threads_username,
            biography=threads_bio,
            profile_pic_url=threads_profile_pic_url,
            threads_id=threads_id,
        )
        user_threads_profile.save()

    # get the followers from the API
    # from 1st June 2024 only available
    since = 1717275600
    metrics = "likes,replies,reposts,quotes,followers_count"
    url_user_insights = f"https://graph.threads.net/v1.0/{threads_id}/threads_insights?since={since}&metric={metrics}&access_token={long_token}"
    user_data = r.get(url_user_insights).json()["data"]

    # look for the followers
    followers = 0
    for d in user_data:
        if d["name"] == "followers_count":
            followers = d["total_value"]["value"]
    # print(user_data)
    # update the followers in the model
    user_profile = ThreadsProfile.objects.filter(username=threads_username)
    user_profile.update(followers=followers)
