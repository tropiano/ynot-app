from django.shortcuts import redirect
from usermodel.models import User
from mainapp.models.threads_profile import ThreadsProfile
from mainapp.models.thread import Thread
from mainapp.management.commands.analyze_user_threads import update_threads
import requests as r
import os
import secrets
from django.shortcuts import redirect
from django.contrib.auth import login

threads_app_secret = os.getenv("THREADS_APP_SECRET")
threads_app_id = os.getenv("THREADS_APP_ID")
threads_scope = os.getenv("THREADS_SCOPE")
threads_redirect_uri = os.getenv("THREADS_REDIRECT_URI")


def generate_oauth_state():
    return secrets.token_urlsafe(16)


def start_oauth_flow(request):

    authorization_url = f"https://threads.net/oauth/authorize?client_id={threads_app_id}&redirect_uri={threads_redirect_uri}&scope={threads_scope}&response_type=code"
    state = generate_oauth_state()
    request.session["oauth_state"] = state
    # Construct authorization URL with state parameter and redirect user
    return redirect(f"{authorization_url}&state={state}")


def authorize(request):

    # user_name = request.user.username
    # print(user_name)

    # check if the user canceled the authorization
    error = request.GET.get("error", None)
    if error:
        return redirect("home")

    # check the state
    state = request.session.pop("oauth_state", None)
    # print(state)
    # print(request)
    # print(request.GET.get("state"))
    wrong_state = state is None or state != request.GET.get("state")
    # print(wrong_state)

    # if no user or wrong state go back to login
    if wrong_state:  # not user_name or
        return redirect("login")

    # get the short access token
    # get the long access token and save
    auth_code = request.GET.get("code")
    # print(auth_code)
    user_name = save_long_token(request, auth_code)
    save_user_info(user_name)
    update_threads(user_name, on_login=True)

    return redirect("dashboard_threads", user=user_name)


def save_long_token(request, auth_code):

    # define the parameters
    get_token_url = "https://graph.threads.net/oauth/access_token"

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
    # get the user_id
    user_id = response.json()["user_id"]

    # get long lived token
    long_token_url = f"https://graph.threads.net/access_token?grant_type=th_exchange_token&client_secret={threads_app_secret}&access_token={short_token}"
    response = r.get(long_token_url)
    long_token = response.json()["access_token"]

    # save the long lived token in the User model
    # need to get the username from the API
    url_user_profile = f"https://graph.threads.net/v1.0/{user_id}?fields=id,username&access_token={long_token}"
    response = r.get(url_user_profile)
    print(response.json())
    threads_username = response.json()["username"]

    # check if the user exists already
    # with the same username
    try:
        user = User.objects.get(username=threads_username)
        # update the user
        user.has_threads = True
        user.threads_token = long_token
        user.save()
    except:
        # create a new user with threads login
        user = User(
            username=threads_username, has_threads=True, threads_token=long_token
        )
        user.save()

    # log the user in
    login(request, user)

    return threads_username


def save_user_info(user_name):

    # get the token to make all requests
    long_token = User.objects.filter(username=user_name).first().threads_token

    # get the threads username and bio
    url_user_profile = f"https://graph.threads.net/v1.0/me?fields=id,username,threads_profile_picture_url,threads_biography&access_token={long_token}"
    response = r.get(url_user_profile)
    # print(response.json())
    threads_username = response.json()["username"]
    threads_id = response.json()["id"]
    if "threads_biography" in response.json():
        threads_bio = response.json()["threads_biography"]
    else:
        threads_bio = ""
    if "threads_profile_picture_url" in response.json():
        threads_profile_pic_url = response.json()["threads_profile_picture_url"]
    else:
        threads_profile_pic_url = ""

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

    # look for the followers, likes, replies
    followers = 0

    for d in user_data:
        if d["name"] == "followers_count":
            followers = d["total_value"]["value"]
        if d["name"] == "likes":
            likes = d["total_value"]["value"]
        if d["name"] == "replies":
            replies = d["total_value"]["value"]

    # print(user_data)
    # update the followers in the model
    user_profile = ThreadsProfile.objects.filter(username=threads_username)
    user_profile.update(followers=followers)
    user_profile.update(likes=likes)
    user_profile.update(replies=replies)
