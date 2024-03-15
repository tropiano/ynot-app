import sys
import os
import pandas as pd
import psycopg2
from transformers import T5Tokenizer, T5ForConditionalGeneration
from collections import defaultdict


model = T5ForConditionalGeneration.from_pretrained("Voicelab/vlt5-base-keywords")
tokenizer = T5Tokenizer.from_pretrained("Voicelab/vlt5-base-keywords")


def read_users():
    """
    Get all users that have not been analyzed yet
    And are paid users
    """
    conn_string = os.environ["DATABASE_URL"]
    # "postgresql://postgres:postgres@localhost:5432/twitter_opt"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    sql = f"""SELECT username, is_processed FROM usermodel_user 
            WHERE is_paid IS True 
            AND is_processed != True 
            AND username NOT LIKE ''
            """
    cursor.execute(sql)

    conn.commit()
    result = cursor.fetchall()
    conn.close()

    return result


def read_tweets(user_name):

    conn_string = os.environ["DATABASE_URL"]
    # "postgresql://postgres:postgres@localhost:5432/twitter_opt"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    sql = f"""SELECT text, score, norm_score FROM mainapp_tweet
            WHERE username = (%s);"""
    cursor.execute(sql, (user_name,))

    conn.commit()
    result = cursor.fetchall()
    conn.close()

    return result


def calc_keywords(result):

    tweet_kws = []

    task_prefix = "Keywords: "

    # only run on the top 100 results
    # order results by the score
    result.sort(key=lambda x: x[1], reverse=True)

    for sample in result[:100]:
        input_sequences = [task_prefix + sample[0]]
        input_ids = tokenizer(
            input_sequences, return_tensors="pt", truncation=True
        ).input_ids
        output = model.generate(input_ids, no_repeat_ngram_size=3, num_beams=4)
        predicted = tokenizer.decode(output[0], skip_special_tokens=True)
        # save it in a dictionary together with the tweet and the score
        tweet_info = {
            "text": sample[0],
            "score": sample[1],
            "norm_score": sample[2],
            "keywords": [p for p in predicted.split(",")],
        }
        tweet_kws.append(tweet_info)

    kws_score = defaultdict(list)
    kws_normscore = defaultdict(list)

    # clean up and fill the scores
    for tweet in tweet_kws:
        kws = tweet["keywords"]
        for kw in kws:
            # clean the kw
            if kw.startswith(" "):
                kw = kw.replace(" ", "", 1)
            # skip the empty kw
            if kw == "" or kw.startswith("@"):
                continue
            kws_score[kw].append(tweet["score"])
            kws_normscore[kw].append(tweet["norm_score"])

    # aggregate the keywords score
    kws_normscore_agg = dict()
    kws_score_agg = dict()
    for kw, scores in kws_normscore.items():
        kws_normscore_agg[kw] = sum(scores)

    for kw, scores in kws_score.items():
        kws_score_agg[kw] = sum(scores)

    return kws_score_agg, kws_normscore_agg


def write_db(kws_score_agg, kws_normscore_agg, user_name):
    conn_string = os.environ["DATABASE_URL"]
    # "postgresql://postgres:postgres@localhost:5432/twitter_opt"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # wipe the table
    sql = "DELETE FROM mainapp_keywords WHERE username=(%s)"
    cursor.execute(sql, (user_name,))

    # exec for each row
    for k1, _ in zip(kws_score_agg, kws_normscore_agg):

        word = k1
        score = kws_score_agg[k1]
        norm_score = kws_normscore_agg[k1]

        sql = f"""INSERT INTO mainapp_keywords (word, score, norm_score, username) 
                VALUES (%s, %s, %s, %s)
                """
        cursor.execute(
            sql,
            (word, score, norm_score, user_name),
        )

    conn.commit()
    conn.close()


def mark_user(user_name):
    conn_string = os.environ["DATABASE_URL"]
    # "postgresql://postgres:postgres@localhost:5432/twitter_opt"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # wipe the table
    sql = """UPDATE usermodel_user
            SET is_processed=True
            WHERE username=(%s)
            """
    cursor.execute(sql, (user_name,))

    conn.commit()
    conn.close()


if __name__ == "__main__":

    all_users = read_users()
    for user in all_users:
        user_name = user[0]
        # extract user tweets
        user_tweets = read_tweets(user_name)
        # calculate keywords score
        user_kws_score, user_kws_normscore = calc_keywords(user_tweets)
        # write on the DB
        write_db(user_kws_score, user_kws_normscore, user_name)
