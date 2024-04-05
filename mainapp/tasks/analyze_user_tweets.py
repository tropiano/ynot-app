import sys
import os
import pandas as pd
import psycopg2
from usermodel.models import User


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
    conn_string = os.environ["DATABASE_URL"]
    # "postgresql://postgres:postgres@localhost:5432/twitter_opt"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # wipe the table
    sql = """DELETE FROM mainapp_tweet WHERE username = (%s)"""
    cursor.execute(sql, (user_name,))

    # exec for each row
    for idx, row in df_full.iterrows():

        sql = f"""INSERT INTO mainapp_tweet (text, time, impressions, score, norm_score, engagements, username) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)"""

        cursor.execute(
            sql,
            (
                row["Tweet text"],
                row["time"],
                row["impressions"],
                row["score"],
                100 * row["norm_score"],
                row["engagements"],
                user_name,
            ),
        )

    # set user to *not processed* (for topics)
    User.objects.filter(username=user_name).update(is_processed=0)

    conn.commit()
    conn.close()


if __name__ == "__main__":

    tweet_file = sys.argv[1]
    user_name = tweet_file.split("/")[-1].split("_")[3]
    df_full = pd.read_csv(tweet_file)
    # apply the function that calculates the score
    df_full["score"] = df_full.apply(lambda x: score(x)[0], axis=1)
    df_full["norm_score"] = df_full.apply(lambda x: score(x)[1], axis=1)
    # write results to the DB
    write_db(df_full, user_name)
