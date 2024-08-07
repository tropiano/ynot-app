from django.core.management.base import BaseCommand
import os
from mainapp.models import KeywordsThreads
from usermodel.models import User
from django.utils import timezone
from mainapp.management.commands.analyze_topics_threads import start_endpoint
from mainapp.management.commands.analyze_topics_threads import read_threads
from mainapp.management.commands.analyze_topics_threads import calc_keywords
from mainapp.management.commands.analyze_topics_threads import write_db
from mainapp.management.commands.analyze_topics_threads import pause_endpoint

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
            self.style.SUCCESS(
                f"{timezone.now()} - Analyzing user topics for the first time"
            )
        )

        # read the latest users and check if they have no topic analysis yet
        # make a quick topic analysis on the latest 10 threads
        all_users = read_latest_users()
        print("Selected latest users (no topics yet)")
        if all_users:
            start_endpoint()
            for user in all_users:
                user_name = user.threads_username
                print(f"Init script - Processing {user_name}")
                # extract user posts
                user_posts = read_threads(user_name, max_threads=10)
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


def read_latest_users():
    """
    Get all users
    Only connected to Threads
    That have no analysis yet
    """

    users_no_topics = []
    print("Selecting latest users (no topics yet)")
    all_users_threads = User.objects.filter(has_threads=True).all()

    for usr in all_users_threads:
        # check if the user has topics analyzed
        user_name = usr.threads_username
        # get the threads from this user
        topics = KeywordsThreads.objects.filter(username=user_name)
        if topics:
            continue
        users_no_topics.append(usr)

    return users_no_topics
