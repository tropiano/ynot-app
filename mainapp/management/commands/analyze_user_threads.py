from django.core.management.base import BaseCommand
from usermodel.models import User
from mainapp.models.thread import Thread
from mainapp.models.threads_profile import ThreadsProfile
import requests as r
from django.utils import timezone


class Command(BaseCommand):
    help = """Analyzes user threads. 
            Collects all user threads and their metrics.
            Get the profile metrics and update them.
            """

    def handle(self, *args, **options):
        # Your command logic here
        self.stdout.write(
            self.style.SUCCESS(f"{timezone.now()} - Analyzing user threads")
        )

        # get all the users
        users = User.objects.filter(has_threads=True)

        for usr in users:
            self.stdout.write(self.style.SUCCESS("New user found"))
            print(f"User {usr.username}")
            update_threads(user_name=usr.username)
            update_threads_profile(user_name=usr.username)
            # update the timestamp
            usr.profile_last_update = timezone.now()
            usr.save()


# define a function
def score(likes, replies, reposts, quotes, views):

    # get score and then normalize by the followers
    score = likes + reposts + quotes + replies

    # fix the division by 0 when tweet has 0 impressions
    # make it at least 1 impression
    # mulitply by 100 because of threads reach algorithm
    return score, (100.0 * score) / max(views, 1)


def update_threads(user_name):

    # get the user long token
    long_token = User.objects.get(username=user_name).threads_token

    # get all saved threads of the user
    user_threads = Thread.objects.filter(username=user_name)
    # get all ids of the saved threads
    user_threads_ids = [t.threadid for t in user_threads]

    # define the metrics
    metrics = "views,likes,replies,reposts,quotes"

    # Make the paginated request and get all new threads
    threads_data = []
    url_user_threads = f"https://graph.threads.net/v1.0/me/threads?fields=id,media_product_type,media_type,media_url,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post&limit=50&access_token={long_token}"
    response = r.get(url_user_threads)
    threads_data.extend(response.json()["data"])

    if "next" in response.json()["paging"]:
        next_url = response.json()["paging"]["next"]
    else:
        next_url = ""

    while next_url:
        response = r.get(next_url)
        threads_data.extend(response.json()["data"])
        if "next" in response.json()["paging"]:
            next_url = response.json()["paging"]["next"]
        else:
            next_url = ""

    # make a call to the API and fill the metrics
    # loop on threads from API
    # if they are already in DB update
    # otherwise save a new one
    for thread in threads_data:
        # define the API url to call
        thread_id = thread["id"]
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
        if int(thread_id) in user_threads_ids:
            print("updating existing thread metrics")
            user_thread = Thread.objects.get(threadid=thread_id)
            user_thread.views = views
            user_thread.reposts = reposts
            user_thread.replies = replies
            user_thread.likes = likes
            user_thread.quotes = quotes
            user_thread.score = post_score
            user_thread.norm_score = post_norm_score
            user_thread.save()
        else:
            print("saving new thread")
            print(thread_id)
            print(type(thread_id))

            # get additional data
            url = thread["permalink"]
            username = thread["username"]
            text = thread["text"]
            time = thread["timestamp"]
            short_code = thread["shortcode"]
            is_quote = thread["is_quote_post"]

            new_thread = Thread(
                threadid=thread_id,
                url=url,
                username=username,
                text=text,
                time=time,
                short_code=short_code,
                is_quote=is_quote,
                views=views,
                reposts=reposts,
                replies=replies,
                likes=likes,
                quotes=quotes,
                score=post_score,
                norm_score=post_norm_score,
            )
            new_thread.save()


def update_threads_profile(user_name):

    # get the user long token
    long_token = User.objects.get(username=user_name).threads_token

    # get the user profile
    user_profile = ThreadsProfile.objects.filter(username=user_name)

    # make a call to the API and fill the metrics
    since = 1717275600  # API available from 1st June 2024
    metrics = "views,likes,replies,reposts,quotes,followers_count"
    url_user_insights = f"https://graph.threads.net/v1.0/me/threads_insights?since={since}&metric={metrics}&access_token={long_token}"

    user_data = r.get(url_user_insights).json()
    # print(user_data)

    for d in user_data["data"]:
        if d["name"] == "followers_count":
            followers = d["total_value"]["value"]
        if d["name"] == "likes":
            likes = d["total_value"]["value"]
        if d["name"] == "replies":
            replies = d["total_value"]["value"]

    user_profile.update(followers=followers)
    user_profile.update(likes=likes)
    user_profile.update(replies=replies)
