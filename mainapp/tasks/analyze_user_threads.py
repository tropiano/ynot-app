import sys
import os
import pandas as pd
import psycopg2
from usermodel.models import User
from mainapp.models.thread import Thread
from mainapp.models.threads_profile import ThreadsProfile
import requests as r


# define a function
def score(likes, replies, reposts, quotes, views):

    # get a score and then normalize by the followers
    score = 0.5 * likes + reposts + quotes + 27 * replies

    # fix the division by 0 when tweet has 0 impressions
    # make it at least 1 impression
    return score, score / max(views, 1)


def update_threads(user_name):

    # get the user long token
    long_token = User.objects.get(username=user_name).threads_token

    # get all threads of the user
    user_threads = Thread.objects.filter(username=user_name)

    # define the metrics
    metrics = "views,likes,replies,reposts,quotes"

    # make a call to the API and fill the metrics
    for thread in user_threads:
        # define the API url to call
        thread_id = thread.threadid
        url_thread_insight = f"https://graph.threads.net/v1.0/{thread_id}/insights?metric={metrics}&access_token={long_token}"
        response = r.get(url_thread_insight)
        data = response.json()["data"]

        for d in data:
            # now fill the DB
            metric = d["name"]
            if metric == "views":
                views = d["values"][0]["value"]
            if metric == "reposts":
                reposts = d["values"][0]["value"]
            if metric == "replies":
                replies = d["values"][0]["value"]
            if metric == "likes":
                likes = d["values"][0]["value"]
            if metric == "quotes":
                quotes = d["values"][0]["value"]

        # calculate scores
        post_score, post_norm_score = score(likes, replies, reposts, quotes, views)

        # update all the metrics in the DBs
        thread.views = views
        thread.reposts = reposts
        thread.replies = replies
        thread.likes = likes
        thread.quotes = quotes
        thread.score = post_score
        thread.norm_score = post_norm_score
        thread.save()


def update_threads_profile(user_name):

    # get the user long token
    long_token = User.objects.get(username=user_name).threads_token

    # get the user profile
    user_profile = ThreadsProfile.objects.filter(username=user_name)

    # make a call to the API and fill the metrics
    since = 1717275600  # 1st June API
    metrics = "views,likes,replies,reposts,quotes,followers_count"
    url_user_insights = f"https://graph.threads.net/v1.0/me/threads_insights?since={since}&metric={metrics}&access_token={long_token}"

    user_data = r.get(url_user_insights).json()

    for d in user_data:
        if d["name"] == "followers_count":
            followers = d["total_value"]["value"]
        if d["name"] == "likes":
            likes = d["total_value"]["value"]
        if d["name"] == "replies":
            replies = d["total_value"]["value"]

    user_profile.update(followers=followers)
    user_profile.update(likes=likes)
    user_profile.update(replies=replies)


if __name__ == "__main__":

    user_name = sys.argv[1]
    update_threads(user_name=user_name)
    update_threads_profile(user_name=user_name)
