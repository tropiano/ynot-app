from django.core.management.base import BaseCommand
import os
from collections import defaultdict
from huggingface_hub import get_inference_endpoint
import requests
from mainapp.models import KeywordsThreads
from usermodel.models import User
from mainapp.models import Thread
from django.utils import timezone


API_URL = "https://y7ypc5d3xkyt8hcg.us-east-1.aws.endpoints.huggingface.cloud"
headers = {
    "Accept": "application/json",
    "Authorization": f"Bearer {os.environ['HF_TOKEN']}",
    "Content-Type": "application/json",
}

conn_string = os.environ["DATABASE_URL"]
# conn_string = "postgresql://postgres:postgres@localhost:5432/twitter_opt"


class Command(BaseCommand):
    help = """Analyzes user topics. 
            Collects all user threads and extract the topic from the endpoint.
            Calculate and update the scores
            """

    def handle(self, *args, **options):
        # Your command logic here
        self.stdout.write(
            self.style.SUCCESS(f"{timezone.now()} - Analyzing user topics")
        )

        # read the latest users and check if they have no topic analysis yet
        # make a quick topic analysis on the latest 10 threads
        all_users = read_threads_users()
        print("Paid Users of Threads read correctly")
        # start endpoint if there are users
        # print(all_users)
        if all_users:
            start_endpoint()
            for user in all_users:
                user_name = user.threads_username
                print(f"Init script - Processing {user_name}")
                # extract user posts
                user_posts = read_threads(user_name)
                print(f"Init script - Read {user_name} Posts- {len(user_posts)} found")
                # calculate keywords score
                user_kws_score, user_kws_normscore = calc_keywords(user_posts)
                print(f"Calculated {user_name} Topics scores")
                # write on the DB
                write_db(user_kws_score, user_kws_normscore, user_name)
                # update the threads last update
                user.threads_last_update = timezone.now()
                # update user as processed
                user.is_processed = True
                user.save()

            # pause endpoint after processing (save costs)
            pause_endpoint()


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


def start_endpoint():
    endpoint = get_inference_endpoint("vlt5-base-keywords-twitopt")
    if endpoint.status != "running" and endpoint.status != "initializing":
        print(f"Endpoint is {endpoint.status}")
        endpoint.resume()
        print("Starting endpoint")
        endpoint.wait()


def pause_endpoint():
    endpoint = get_inference_endpoint("vlt5-base-keywords-twitopt")
    endpoint.pause()


# model = T5ForConditionalGeneration.from_pretrained("Voicelab/vlt5-base-keywords")
# tokenizer = T5Tokenizer.from_pretrained("Voicelab/vlt5-base-keywords")


def read_threads_users():
    """
    Get all paid users
    Only connected to Threads
    """

    print("Selecting all paid or free trial thread users")
    all_users_threads = (
        User.objects.filter(has_threads=True, is_paid=True)
        | User.objects.filter(has_threads=True, is_free_trial=True)
    ).all()

    # loop and save username
    users_no_topics = [usr for usr in all_users_threads]

    return users_no_topics


def read_threads(user_name):

    # select latest 100 threads
    posts = Thread.objects.filter(username=user_name).all().order_by("-time")[:100]

    return posts


def calc_keywords(result):
    # Based on text, score, norm_score
    # Calculate the topics score

    thread_kws = []

    task_prefix = "Keywords: "

    for sample in result:
        # skip if the tweet is a reply and starts with @
        if sample.text.startswith("@"):
            continue
        input_sequences = task_prefix + sample.text
        predicted = query({"inputs": input_sequences, "parameters": {}})[0][
            "generated_text"
        ]
        # save it in a dictionary together with the post and the score
        info = {
            "text": sample.text,
            "score": sample.score,
            "norm_score": sample.norm_score,
            "keywords": [p for p in predicted.split(",")],
        }
        thread_kws.append(info)

    kws_score = defaultdict(list)
    kws_normscore = defaultdict(list)

    # clean up and fill the scores
    for thread in thread_kws:
        kws = thread["keywords"]
        for kw in kws:
            # clean the kw
            if kw.startswith(" "):
                kw = kw.replace(" ", "", 1)
            # skip the empty kw
            if kw == "" or kw.startswith("@"):
                continue
            # use lowercase
            kws_score[kw.lower()].append(thread["score"])
            kws_normscore[kw.lower()].append(thread["norm_score"])

    # aggregate the keywords score
    kws_normscore_agg = dict()
    kws_score_agg = dict()
    for kw, scores in kws_normscore.items():
        kws_normscore_agg[kw] = sum(scores)

    for kw, scores in kws_score.items():
        kws_score_agg[kw] = sum(scores)

    return kws_score_agg, kws_normscore_agg


def write_db(kws_score_agg, kws_normscore_agg, user_name):

    # delete all user topics first
    user_topics = KeywordsThreads.objects.filter(username=user_name)
    user_topics.delete()

    # save the topics in the DB
    # exec for each row
    for k1, _ in zip(kws_score_agg, kws_normscore_agg):

        word = k1
        score = kws_score_agg[k1]
        norm_score = kws_normscore_agg[k1]

        KeywordsThreads(
            word=word, score=score, norm_score=norm_score, username=user_name
        ).save()
