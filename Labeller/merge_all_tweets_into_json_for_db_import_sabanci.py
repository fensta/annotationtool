"""
Creates a json file containing all tweets that should be imported into MongoDB.
This json file can be uploaded to OpenShift to import it into the respective DB.

For Sabanci: create a dataset for group L comprising 500 and 1000 tweets, where
the 500 tweets contain the all of the 200 tweets annotated by S and M.

Copy the created file into the /tmp directory of the server (e.g. using
FileZilla) and then import it into MongoDB:
mongoimport --type json --host $OPENSHIFT_MONGODB_DB_HOST --port $OPENSHIFT_MONGODB_DB_PORT -u $OPENSHIFT_MONGODB_DB_USERNAME -p $OPENSHIFT_MONGODB_DB_PASSWORD -d $OPENSHIFT_APP_NAME -c tweets < /tmp/tweets.json

Copy on localhost:
mongoimport -d annotationtool -c tweets /tmp/tweets.json

Delete existing tweet collection before:
use annotation_tool;
db.tweets.dropDatabase();

"""
import json
import os


from pymongo import MongoClient


def get_annotated_tweets_by_user(user_collection, username):
    """
    Finds the tweet IDs of the annotated tweets by a certain annotator.

    Parameters
    ----------
    user_collection: pymongo.collection.Collection - collection in which users
    are stored.
    username: string - name of the user for which the annotated tweets should
    be found.

    Returns
    -------
    List of ObjectIds.
    Each ID represents a tweet ID.

    """
    user = user_collection.find_one({"username": username})
    return user["annotated_tweets"]


def get_all_tweets_of_dataset(tweet_collection):
    """
    Returns the number of tweets in a DB.

    Parameters
    ---------
    tweet_collection: pymongo.collection.Collection - tweet collection.

    Returns
    -------
    int.
    Total number of tweets in collection.

    """
    return tweet_collection.count()


def get_tweet_name(tweet_collection, t_id):
    """
    Returns the name of the tweet as a file. It has the pattern
    <tweet_author>_<tweet_id>.txt.

    Parameters
    ----------
    tweet_collection: pymongo.collection.Collection - tweet collection.
    t_id: ObjectId - ID of the tweet.

    Returns
    -------
    List of strings.
    Each string represents the file name of a tweet.

    """
    tweet = tweet_collection.find_one({"_id": t_id})
    user_id = tweet["user"]["id_str"]
    tweet_id = tweet["id_str"]
    return "{}_{}.txt".format(user_id, tweet_id)


def get_previously_annotated_tweets_by(username, user_coll, tweet_coll):
    """
    Finds all tweets that were previously annotated by an annotator.

    Parameters
    ----------
    username: string - username of annotator in annotation tool.
    user_coll: pymongo.collection.Collection - collection containing the
    annotators.
    tweet_coll: pymongo.collection.Collection - collection containing the
    tweets.

    Returns
    -------
    List of strings.
    Each string represents a tweet name. It has the following pattern:
    <user_id>_<tweet_id>.txt

    """
    annotated_tweet_ids = get_annotated_tweets_by_user(user_coll, username)
    tweet_names = []
    for t_id in annotated_tweet_ids:
        tweet_names.append(get_tweet_name(tweet_coll, t_id))
    return tweet_names


def get_all_200_tweets_from_s_m(tweet_coll):
    """
    Finds a list of all tweets in the dataset.

    Parameters
    ----------
    tweet_coll: pymongo.collection.Collection - collection containing the
    tweets.

    Returns
    -------
    List of Tweet objects.

    """
    return tweet_coll.find({})


def get_all_200_tweet_names_from_s_m(tweet_coll):
    """
    Finds the file names of the tweets included in the S/M dataset (200 tweets).

    Parameters
    ----------
    tweet_coll: pymongo.collection.Collection - collection containing the
    tweets.

    """
    names = []
    for tweet in get_all_200_tweets_from_s_m(tweet_coll):
        user_id = tweet["user"]["id_str"]
        tweet_id = tweet["id_str"]
        names.append("{}_{}.txt".format(user_id, tweet_id))
    return names

if __name__ == "__main__":
    # Additional fields that must be present for each tweet
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

    # The latest backup of the database is stored locally in a DB called "test"
    connection = MongoClient()
    # Our database
    db = connection.test
    # Collection of users
    user_coll = db.user
    # Collection of tweets of the S/M dataset (200 tweets)
    tweet_coll = db.tweets
    tweet_dir = "/media/data/dataset/debate1_trump_vs_clinton_final_dataset/"

    # Store only the first MAX_TWEETS at most
    MAX_TWEETS = 500
    out_name = "500_sabanci.json"
    out_name2 = "1000.json"
    match = []
    no_match = []
    # All tweets are stored in this file
    file_content = []
    # 1. Add all the tweets from S/M dataset
    existing_tweets = get_all_200_tweet_names_from_s_m(tweet_coll)
    print "existing tweets:"
    for n in existing_tweets:
        print n
    for tweets, tweet in enumerate(os.listdir(tweet_dir)):
        print tweet
        if tweet in existing_tweets:
            tweet_path = os.path.join(tweet_dir, tweet)
            with open(tweet_path, "rb") as f:
                tweet_content = json.load(f)
                tweet_content.update(ADDITIONAL_FIELDS)
                file_content.append(tweet_content)
                MAX_TWEETS -= 1
    print "now add the remaining {} tweets".format(MAX_TWEETS)
    # 2. Add remaining 300 tweets
    for tweets, tweet in enumerate(os.listdir(tweet_dir)):
        tweet_path = os.path.join(tweet_dir, tweet)
        with open(tweet_path, "rb") as f:
            if MAX_TWEETS > 0 and tweet not in existing_tweets:
                tweet_content = json.load(f)
                tweet_content.update(ADDITIONAL_FIELDS)
                file_content.append(tweet_content)
                MAX_TWEETS -= 1
    print "#tweets:", len(file_content)
    with open(out_name, "wb") as f:
        for tweet in file_content:
            json.dump(tweet, f)
            # Each tweet must be on a separate line, otherwise MongoDB treats it
            # as 1 object
            f.write("\n")
