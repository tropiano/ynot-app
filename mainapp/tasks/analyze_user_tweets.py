import sys
import os
import pandas as pd
import psycopg2
from usermodel.models import User
from mainapp.models.tweet import Tweet


# define a function
def score(row):

    likes = row["likes"]
    retweets = row["retweets"]
    replies = row["replies"]
    expands = row["detail expands"]
    engagement = min(expands, max(likes, replies))
    profile = row["user profile clicks"]
    profile_engagement = min(profile, max(likes, replies))
    impressions = row["impressions"]

    # get a score and then normalize by the followers
    score = (
        0.5 * likes
        + retweets
        + 11 * engagement
        + 12 * profile_engagement
        + 27 * replies
    )

    # fix the division by 0 when tweet has 0 impressions
    # make it at least 1 impression
    return score, score / max(impressions, 1)


def write_db(df_full, user_name):

    # rewritten to use Django ORM
    # first of all delete all tweets
    # from the user
    Tweet.objects.filter(username=user_name).delete()

    # loop and save all tweets
    for idx, row in df_full.iterrows():

        tweet = Tweet(
            text=row["Tweet text"],
            time=row["time"],
            impressions=row["impressions"],
            score=row["score"],
            norm_score=100 * row["norm_score"],
            engagements=row["engagements"],
            username=user_name,
        )

        tweet.save()

    # set user to *not processed* (for topics)
    User.objects.filter(username=user_name).update(is_processed=0)


if __name__ == "__main__":

    tweet_file = sys.argv[1]
    user_name = tweet_file.split("/")[-1].split("_")[3]
    df_full = pd.read_csv(tweet_file)
    # apply the function that calculates the score
    df_full["score"] = df_full.apply(lambda x: score(x)[0], axis=1)
    df_full["norm_score"] = df_full.apply(lambda x: score(x)[1], axis=1)
    # write results to the DB
    write_db(df_full, user_name)
