"""
Creates a json file containing all tweets that should be imported into MongoDB.
This json file can be uploaded to OpenShift to import it into the respective DB.

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
    db = connection.mdsmannotationtool
    # Collection of users
    user_coll = db.user
    # Collection of tweets
    tweet_coll = db.tweets
    annotated = get_previously_annotated_tweets_by("harish\u002epakala@ovgu\u002ede",
                                                   user_coll, tweet_coll)

    # tweet_dir = "/media/ssd/phd/greece/test/mergedTweetData/"
    # tweet_dir = "/media/ssd/phd/greece/smallDataset/dataset/"
    # tweet_dir = "/media/data/dataset/trump/collected_tweets/"
    # Contains tweets with difficult characters and formattings
    # tweet_dir = "/media/data/dataset/anno_tool_test"
    # tweet_dir = "/media/data/dataset/debate1_trump_vs_clinton_final_dataset/"
    tweet_dir = "/media/data/dataset/debate1_trump_vs_clinton_final_dataset_s_m/"

    # Store only the first MAX_TWEETS at most
    MAX_TWEETS = 1000
    # True if an existing M-run should be turned into an L-run
    # In that case the local DB must be up-to-date
    TURN_M_INTO_L = True
    out_name = "50_tweets_harish.json"
    match = []
    no_match = []
    # All tweets are stored in this file
    file_content = []
    if TURN_M_INTO_L:
        for tweets, tweet in enumerate(os.listdir(tweet_dir)):
            # If tweet wasn't annotated by a user before
            if tweet not in annotated:
                tweet_path = os.path.join(tweet_dir, tweet)
                with open(tweet_path, "rb") as f:
                    tweet_content = json.load(f)
                    tweet_content.update(ADDITIONAL_FIELDS)
                    file_content.append(tweet_content)
            else:
                match.append(tweet)
        print "# existing tweets in directory: ", len(set(os.listdir(tweet_dir)))
        print "# unannotated tweets: ", len(file_content)
        print "# annotated tweets: ", len(set(annotated))
        print "# matches: ", len(match)
        s1 = set(match)
        s2 = set(annotated)
        no_match = s2.difference(s1)
        # For how many annotated tweets does no match exist in dataset?
        # (should be 0)?
        print len(no_match), no_match
    else:
        for tweets, tweet in enumerate(os.listdir(tweet_dir)):
            print tweet
            tweet_path = os.path.join(tweet_dir, tweet)
            with open(tweet_path, "rb") as f:
                if tweets < MAX_TWEETS:
                    tweet_content = json.load(f)
                    tweet_content.update(ADDITIONAL_FIELDS)
                    file_content.append(tweet_content)
    with open(out_name, "wb") as f:
        for tweet in file_content:
            json.dump(tweet, f)
            # Each tweet must be on a separate line, otherwise MongoDB treats it
            # as 1 object
            f.write("\n")
