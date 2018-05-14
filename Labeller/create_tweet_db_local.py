"""
Test file for MongoDB integration with Python

1. Start MongoDB service:
 go to E:/Programs/MongoDB
 type mongod -f mongo-yaml.conf

2. Start MongoDB: mongo

3. Run test.py now that a connection is open
"""
"""
This file creates the tweet DB using MongoDB and stores all tweets appropriately
"""
import codecs
import json
import os
import shutil
from pymongo import MongoClient
from datetime import datetime, timedelta
from email.utils import parsedate_tz


def create_testcase(src_tweet, src_ne, dst_tweet, dst_ne, tweets):
    """
    Copies 3 tweets (and the extracted named entities) into a test directory.

    Parameters
    ----------
    src_tweet: Root directory under which the analyzed tweets are stored.
    src_ne: Root directory under which the extracted named entities are stored.
    dst_tweet: Root directory under which the analyzed tweets should be stored.
    dst_ne: Root directory under which the extracted named entities should be
    stored.
    tweets: Number of tweets to be used for the test.

    """
    for ctr, t in enumerate(os.listdir(src_tweet)):
        if ctr < tweets:
            src_ne_p = os.path.join(src_ne, t)
            src_tweet_p = os.path.join(src_tweet, t)
            dst_ne_p = os.path.join(dst_ne, t)
            dst_tweet_p = os.path.join(dst_tweet, t)
            shutil.copy(src_ne_p, dst_ne_p)
            shutil.copy(src_tweet_p, dst_tweet_p)
        else:
            break


def _read_tweet(tweet_path):
    """

    Reads in a tweet for further processing.

    Parameters:
    -----------
    tweet_path: Path to a tweet to be loaded.

    Returns:
    --------
    The JSON-encoded content of the tweet.

    """
    unicode_json = {}
    with codecs.open(tweet_path, "r", "utf-8-sig") as f:
        unicode_json = json.load(f)
    return unicode_json


def _write_tweet(data, dst):
    """
    Writes the tweet encoded in UTF-8 into the specified file in JSON format.

    Parameters
    ----------
    data: Dictionary containing the data to be stored in JSON format.
    dst: Path under which the data should be stored.

    """
    with codecs.open(dst, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)


def merge_tweets(tweet_p, ne_p, dst_p):
    """
    Merges all data about collected tweets. This means not only the metadata
    from Twitter are stored, but also the data obtained from
    All metadata related to named entities might be accessed using the
    additional attribute "alchemy" in the merged tweets.

    Parameters
    ----------
    tweet_p: Root directory in which the analyzed tweets are stored.
    ne_p: Root directory in which the extracted named entities are stored.
    dst_p: Root directory in which the merged data should be stored

    """
    prefix = "alchemy"
    for t in os.listdir(tweet_p):
        t_p = os.path.join(tweet_p, t)
        n_p = os.path.join(ne_p, t)
        dst = os.path.join(dst_p, t)
        data = _read_tweet(t_p)
        data[prefix] = _read_tweet(n_p)
        _write_tweet(data, dst)


def delete_db(connection, name):
    """
    Deletes a MongoDB database.

    Parameters
    ----------
    connection: Connection to MongoDB
    name: Name of the DB to be deleted.

    """
    connection.drop_database(name)


def delete_collection(db, name):
    """
    Deletes a collection from the database.

    Parameters
    ----------
    db: MongoDB database from which the collection (= table) should be deleted.
    name: Name of the collection to be deleted.
    """
    db.drop_collection(name)


def get_connection(host, port):
    """
    Returns a connection to MongoDB with the given configuration.

    Parameters
    ----------
    host: Host address used for opening the connection.
    port: Port used to open the connection.

    Returns
    -------
    Connection to the database.

    """
    client = MongoClient(host=host, port=port)
    return client


def get_db(connection):
    """
    Gets the MongoDB database.

    Parameters
    ----------
    connection: Connection to the database.

    Returns
    -------
    MongoDB database instance.

    """
    db = connection.annotation_tool
    print connection.database_names()
    print "collections in annotation_tool:", db.collection_names()
    return db


def populate_annotator_db(db):
    """
    Creates a test user named "a" with password "a".

    Parameters
    ----------
    db: Database into which the data should be stored.

    """
    data = {
        "email": "foo@bar.com",
        "username": "foo@bar.com",
        "password": None,
        "al_strategy": "RS",
        "group": "S",
        "tweets_per_session": 50,
        "annotated_in_session": 0,
        "tweets_to_annotate": 30,
        "next_tweet": None,
        # "degree_program": "a",
        # "sex": "male",
        # "nationality": "a",
        # "semesters": 1,
        # "faculty": "FENS",
        # "level": "BA",
        "annotated_tweets": [],
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "last_login": None,
        "date_joined": None,
        "user_permissions": None,
        "_cls": "User.Annotator",
    }
    db.user.insert(data)


def populate_tweet_db(p, db):
    """
    Fills the empty DB with all the tweets to be stored.

    Parameters
    ----------
    p: Root directory in which all tweets (with all metadata) are stored.
    db: Database into which the data should be stored.

    """
    for t in os.listdir(p):
        tweet_path = os.path.join(p, t)
        data = _read_tweet(tweet_path)
        # Add additional entries per tweet
        data.update(ADDITIONAL_FIELDS)
        add_tweet(db.tweets, data)

# def add_additional_fields(data, fields):
#     """
#     Adds additional fields or key-value pairs to the data before storing the
#     tweet in the DB.
#
#     Parameters
#     ----------
#     data: Dictionary containing the data to be stored in the DB.
#     fields: Dictionary containing the fields to be added to each tweet.
#
#     Returns
#     -------
#     Data enriched with the new entries.
#
#     """
#     return data.extend(fields)


def add_tweet(coll, data):
    """
    Adds a tweet to a DB.

    Parameters
    ----------
    coll: Collection (table) into which the tweet should be inserted.
    data: Tweet data to be stored.

    """
    coll.insert(data)

# http://stackoverflow.com/questions/7703865/going-from-twitter-date-to-python-datetime-date
def to_datetime(datestring):
    """
    Converts a string containing a data into a date object. It considers the
    time zone offset as opposed to existing functions (see link above).

    Parameters
    ----------
    datestring: String representation of date.

    Returns
    -------
    Date object.

    """
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])


def show_collection(coll):
    """
    Displays all entries in a given collection.

    Parameters
    ----------
    coll: Table for which the content is displayed.

    """
    for entry in coll.find():
        entry["_id"] = str(entry["_id"])  # Convert ObjectId to string
        print entry["_id"]
        print(json.dumps(entry, indent=4))

if __name__ == "__main__":
    src_tweet_path = "/media/ssd/phd/greece/analyzedTweets/"
    src_ne_path = "/media/ssd/phd/greece/namedEntities/"
    dst_tweet_path = "/media/ssd/phd/greece/test/analyzedTweets/"
    dst_ne_path = "/media/ssd/phd/greece/test/namedEntities/"
    merged_dir = "/media/ssd/phd/greece/test/mergedTweetData/"
    CREATE_MERGED_TWEET_DIR = False
    DB_PORT = 27017
    DB_HOST = "localhost"

    # Fields that need to be added for each tweet. See models.Tweet for all
    # fields.
    ADDITIONAL_FIELDS = {
        "relevance_label": {},
        "opinion_label": {},
        "relevance_time": {},
        "fact_time": {},
        "opinion_time": {},
        "confidence_relevance": {},
        "confidence_fact": {},
        "confidence_opinion": {},
        "confidence_relevance_time": {},
        "confidence_fact_time": {},
        "confidence_opinion_time": {},
        "annotation_timestamp": {},
        "succ": {},
        "pred": {},
    }

    if CREATE_MERGED_TWEET_DIR:
        create_testcase(src_tweet_path, src_ne_path, dst_tweet_path,
                        dst_ne_path, 10)
        merge_tweets(dst_tweet_path, dst_ne_path, merged_dir)
    else:
        c = get_connection(DB_HOST, DB_PORT)
        print "Delete existing table annotation_tool"
        delete_db(c, "annotation_tool")
        print "Rebuild annotation_tool from scratch"
        db = get_db(c)
        print c.database_names()
        print "Delete existing table/collection 'tweets'"
        delete_collection(db, "tweets")
        print "Rebuild collection 'tweets' from scratch"
        print db.collection_names()
        populate_tweet_db(merged_dir, db)
        # populate_annotator_db(db)
        # print get_country(db)
        show_collection(db.tweets)
        # show_collection(db.user)


    # s = 'Tue Mar 29 08:11:25 +0000 2011'
    # print to_datetime(s)

