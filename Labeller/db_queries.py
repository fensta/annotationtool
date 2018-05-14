from models import Annotator, Tweet
"""
This file contains all queries for MongoEngine.

findOne() = Db.objects.get(query) -> returns single object of type Db
find() = Db.objects(query) -> returns query set with possibly multiple Db
objects
"""


# Leave these 2 methods in here and don't put them into util.py because
# otherwise it would become a cyclic dependency!
def username_to_mongo(username):
    """
    Converts the username (= email address) into a string in which all dots
    are replaced by the unicode equivalent (\u002e) because MongoDB can't
    handle dots in dictionary keys.

    Parameters
    ----------
    username: Name of annotator to be converted.

    Returns
    -------
    Transformed username.

    """
    username = username.decode("utf8").replace(u"\u002e", "\u002e")
    return username


def username_to_email(username):
    """
    Converts the encoded username back into a displayable URL by replacing (
    \u002e) with a dot again.

    Parameters
    ----------
    username: Name of annotator to be converted.

    Returns
    -------
    Transformed username.

    """
    username = username.decode("utf8").replace("\u002e", u"\u002e").encode(
        "utf8")
    return username


def get_tweet_from_db(tweet_id):
    """
    Returns the tweet with the given ID from the DB.

    Parameters
    ----------
    tweet_id: String of the tweet ID.

    Returns
    -------
    Tweet object with the given ID. Returns None if tweet_id is None.

    """
    if tweet_id is not None:
        # No need to return full documents -> a subset of fields suffices
        # return Tweet.objects.get(pk=tweet_id)
        return Tweet.objects.exclude("user").\
            exclude("quoted_status").exclude("geo").exclude("retweeted_status")\
            .exclude("entities").exclude("extended_entities").get(pk=tweet_id)
    return None


def get_annotator_from_db(username):
    """
    Returns the annotator object from the DB.

    Parameters
    ----------
    username: User name of the annotator.

    Returns
    -------
    Annotator object.

    """
    try:
        return Annotator.objects.get(username=username_to_mongo(username))
    except Annotator.DoesNotExist as e:
        print e.message


def get_all_tweet_ids_from_db(username):
    """
    Returns a list of all tweet IDs in the DB.

    Parameters
    ----------
    username: User name of the annotator.

    Returns
    -------
    List of tweet IDs.

    """
    ids = []
    tweets = Tweet.objects.all()
    for t in tweets:
        ids.append(t.id)
    return ids


def update_annotated_tweets_in_db(tweet_id, uname):
    """
    Updates the 'annotated_tweets' field of an annotator with the recently
    annotated tweet ID. Note that the ID will be added only once to the list.

    Parameters
    ----------
    tweet_id: ID of tweet to be updated.
    uname: User name of the annotator.

    """
    try:
        # User might annotate same tweet multiple times by going clicking on
        # 'previous/next', so we only need 1 entry
        Annotator.objects.get(username=username_to_mongo(uname)).update(
            push__annotated_tweets=tweet_id)
    except Annotator.DoesNotExist as e:
        print e.message


def update_unlabeled_tweets_in_db(tweet_id, uname):
    """
    Updates the 'unlabeled_tweets' field of an annotator by removing the
    recently annotated tweet ID.

    Parameters
    ----------
    tweet_id: ID of tweet to be updated.
    uname: User name of the annotator.

    """
    try:
        # User might annotate same tweet multiple times by going clicking on
        # 'previous/next', so we only need 1 entry
        Annotator.objects.get(username=username_to_mongo(uname)).update(
            pull__unlabeled_tweet_ids=tweet_id)
    except Annotator.DoesNotExist as e:
        print e.message


def decrement_unlabeled_tweets_in_db(uname):
    """
    Decrements the field 'unlabeled_tweets' in the DB.

    Parameters
    ----------
    uname: User name of the annotator.

    """
    uname = username_to_mongo(uname)
    Annotator.objects.get(username=uname).update(dec__unlabeled_tweets=1)


def init_annotator(username):
    """
    Initializes 'unlabeled_tweet_ids', 'unlabeled_tweets', and 'total_tweets' of
    an annotator.

    Raises
    ------
    AssertionError: If tweet DB is empty.

    """
    ids = get_all_tweet_ids_from_db(username)
    # Can only be 0 if Tweet DB is empty -> in that case create DB and
    # initialize annotator afterwards
    if len(ids) == 0:
        raise AssertionError()
    Annotator.objects.get(username=username).update(
                                push_all__unlabeled_tweet_ids=ids)
    Annotator.objects.get(username=username).update(
        set__unlabeled_tweets=len(ids))
    Annotator.objects.get(username=username).update(
        set__total_tweets=len(ids))


def update_next_tweet_in_db(tweet_id, uname):
    """
    Updates the "next_tweet" field of the annotator, meaning the annotator
    will label the specified tweet next.

    Parameters
    ----------
    tweet_id: ID of tweet to be updated.
    anno: Annotator object that should label the tweet.

    """
    Annotator.objects.get(username=username_to_mongo(uname)).update(
        set__next_tweet=tweet_id)


# def get_all_annotated_tweets_from_db():
#     """
#     Returns all tweets that were already annotated (i.e.'annotation_timestamp'
#     isn't empty).
#
#     Returns
#     -------
#     Query set containing all annotated tweet objects.
#
#     """
#     return Tweet.objects(annotation_timestamp__not__ne=None)


# def get_all_unlabeled_tweets_in_db(username):
#     """
#     Returns all unlabeled tweets (i.e. 'annotation_timestamp' is empty) for a
#     specific user.
#
#     Parameters
#     ----------
#     username: Name of the annotator for whom all unlabeled tweets should be
#     retrieved.
#
#     Returns
#     -------
#     Query set containing all annotated tweet objects.
#
#     """
#     # all query operators: http://docs.mongoengine.org/guide/querying.html
#     # return Tweet.objects(annotation_timestamp__username__exists=False)
#     try:
#         username = username_to_mongo(username)
#         return Tweet.objects(**{"annotation_timestamp__" + username +
#                                 "__exists": False})
#     except Exception as e:
#         print str(e)
#         return None


def update_annotation_timestamp_in_db(tweet_id, username, anno_date):
    """
    Updates the 'annotation_timestamp' field of the tweet in the DB.

    Parameters
    ----------
    tweet_id: ID of tweet to be updated.
    username: Name of user for whom the timestamp should be added
    anno_date: Timestamp at which the tweet was annotated. It must be a datetime
    object.

    """
    # Tweet.objects.get(id=tweet_id).update(set__annotation_timestamp=anno_date)
    # Store for the tweet a user name and when he/she annotated the tweet
    Tweet.objects.get(id=tweet_id).update(
            **{"set__annotation_timestamp__" + username_to_mongo(username):
               anno_date})


def update_relevance_label_in_db(label, username, tweet_id):
    """
    Updates the label 'relevance_label' in the DB.

    Parameters
    ----------
    label: Label to be stored for the tweet.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    # Tweet.objects.get(id=tweet_id).update(set__relevance_label=label)
    try:
        Tweet.objects.get(id=tweet_id).update(
                **{"set__relevance_label__" + username_to_mongo(username):
                    label})
    except Exception as e:
        print "update relevance label error", e, e.message


def update_opinion_label_in_db(label, username, tweet_id):
    """
    Updates the label 'opinion_label' in the DB.

    Parameters
    ----------
    label: Label to be stored for the tweet.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    # Tweet.objects.get(id=tweet_id).update(set__opinion_label=label)
    Tweet.objects.get(id=tweet_id).update(
            **{"set__opinion_label__" + username_to_mongo(username): label})


def remove_opinion_label_in_db(label, username, tweet_id):
    """
    Removes the label 'opinion_label' of a user from the DB. In other words,
    it simply removes the user from that dictionary.

    Parameters
    ----------
    label: Label to be removed.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    Tweet.objects.get(id=tweet_id).update(
            **{"unset__opinion_label__" + username_to_mongo(username): label})


def update_fact_label_in_db(label, username, tweet_id):
    """
    Updates the label 'fact_label' in the DB.

    Parameters
    ----------
    label: Label to be stored for the tweet.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    try:
        username = username_to_mongo(username)
        # Tweet.objects.get(id=tweet_id).update(set__fact_label=label)
        Tweet.objects.get(id=tweet_id).update(
                **{"set__fact_label__" + username: label})
    except Exception as e:
        print "update fact label error", e, e.message


def update_relevance_time_in_db(t, username, tweet_id):
    """
    Updates the time 'relevance_time' needed for the annotator to assign the
    username: Name of annotator who labeled tweet.
    label 'relevance_label' in the DB.

    Parameters
    ----------
    t: Time in seconds.
    tweet_id: ID of tweet to be updated..

    """
    # Tweet.objects.get(id=tweet_id).update(set__relevance_time=t)
    try:
        username = username_to_mongo(username)
        Tweet.objects.get(id=tweet_id).update(
                **{"set__relevance_time__" + username: t})
    except Exception as e:
        print "exception in update_relevance_confidence_time", e, e.message


def update_fact_time_in_db(t, username, tweet_id):
    """
    Updates the time 'fact_time' needed for the annotator to assign the
    label 'fact_label' in the DB.

    Parameters
    ----------
    t: Time in seconds.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated..

    """
    # Tweet.objects.get(id=tweet_id).update(set__fact_time=t)
    username = username_to_mongo(username)
    Tweet.objects.get(id=tweet_id).update(
            **{"set__fact_time__" + username: t})


def update_opinion_time_in_db(t, username, tweet_id):
    """
    Updates the time 'opinion_time' needed for the annotator to assign the
    label 'opinion_label' in the DB.

    Parameters
    ----------
    t: Time in seconds.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    # Tweet.objects.get(id=tweet_id).update(set__opinion_time=t)
    username = username_to_mongo(username)
    Tweet.objects.get(id=tweet_id).update(
            **{"set__opinion_time__" + username: t})


def remove_opinion_time_in_db(t, username, tweet_id):
    """
    Removes the user from 'opinion_time'.

    Parameters
    ----------
    t: Time in seconds.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    username = username_to_mongo(username)
    Tweet.objects.get(id=tweet_id).update(
            **{"unset__opinion_time__" + username: t})


def update_relevance_confidence_in_db(conf, username, tweet_id):
    """
    Updates the time the annotator needed to decide about the confidence of
    'confidence_relevance' in DB.

    Parameters
    ----------
    conf: Confidence value - either "high" or "Low".
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    # Tweet.objects.get(id=tweet_id).update(set__confidence_relevance=conf)
    username = username_to_mongo(username)
    Tweet.objects.get(id=tweet_id).update(
            **{"set__confidence_relevance__" + username: conf})


def update_fact_confidence_in_db(conf, username, tweet_id):
    """
    Updates the time the annotator needed to decide about the confidence of
    'confidence_fact' in DB.

    Parameters
    ----------
    conf: Confidence value - either "high" or "Low".
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    # Tweet.objects.get(id=tweet_id).update(set__confidence_fact=conf)
    username = username_to_mongo(username)
    Tweet.objects.get(id=tweet_id).update(
            **{"set__confidence_fact__" + username: conf})


def update_opinion_confidence_in_db(conf, username, tweet_id):
    """
    Updates the time the annotator needed to decide about the confidence of
    'confidence_opinion' in DB.

    Parameters
    ----------
    conf: Confidence value - either "high" or "Low".
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    # Tweet.objects.get(id=tweet_id).update(set__confidence_opinion=conf)
    username = username_to_mongo(username)
    Tweet.objects.get(id=tweet_id).update(
            **{"set__confidence_opinion__" + username: conf})


def remove_opinion_confidence_in_db(conf, username, tweet_id):
    """
    Removes 'confidence_opinion' of the user from the DB.

    Parameters
    ----------
    conf: Confidence value - either "high" or "Low".
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    username = username_to_mongo(username)
    Tweet.objects.get(id=tweet_id).update(
            **{"unset__confidence_opinion__" + username: conf})


def update_relevance_confidence_time_in_db(t, username, tweet_id):
    """
    Updates the time 'confidence_relevance_time' needed for the
    annotator to assign the label 'relevance_confidence' in the DB.

    Parameters
    ----------
    t: Time in seconds.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    # Tweet.objects.get(id=tweet_id).update(set__confidence_relevance_time=t)
    try:
        username = username_to_mongo(username)
        Tweet.objects.get(id=tweet_id).update(
                **{"set__confidence_relevance_time__" + username: t})
    except Exception as e:
        print "exception in update_relevance_confidence_time", e, e.message


def update_fact_confidence_time_in_db(t, username, tweet_id):
    """
    Updates the time 'confidence_fact_time' needed for the
    annotator to assign the label 'relevance_confidence' in the DB.

    Parameters
    ----------
    t: Time in seconds.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    # Tweet.objects.get(id=tweet_id).update(set__confidence_fact_time=t)
    username = username_to_mongo(username)
    Tweet.objects.get(id=tweet_id).update(
            **{"set__confidence_fact_time__" + username: t})


def update_opinion_confidence_time_in_db(t, username, tweet_id):
    """
    Updates the time 'confidence_opinion_time' needed for the
    username: Name of annotator who labeled tweet.
    annotator to assign the label 'opinion_confidence' in the DB.

    Parameters
    ----------
    t: Time in seconds.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    # Tweet.objects.get(id=tweet_id).update(set__confidence_opinion_time=t)
    username = username_to_mongo(username)
    Tweet.objects.get(id=tweet_id).update(
            **{"set__confidence_opinion_time__" + username: t})


def remove_opinion_confidence_time_in_db(t, username, tweet_id):
    """
    Removes 'confidence_opinion_time' of the user from the DB.

    Parameters
    ----------
    t: Time in seconds.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet to be updated.

    """
    username = username_to_mongo(username)
    Tweet.objects.get(id=tweet_id).update(
            **{"unset__confidence_opinion_time__" + username: t})


def increment_annotated_in_session_in_db(uname):
    """
    Increments the field 'annotated_in_session'.

    Parameters
    ----------
    uname: Username of the annotator.

    """
    uname = username_to_mongo(uname)
    Annotator.objects.get(username=uname).update(inc__annotated_in_session=1)


def update_annotated_in_session_in_db(no, uname):
    """
    Increments the field 'annotated_in_session'.

    Parameters
    ----------
    no: New number to which the field should be updated to.
    uname: Username of the annotator.

    """
    uname = username_to_mongo(uname)
    Annotator.objects.get(username=uname).update(set__annotated_in_session=no)


def update_tweets_per_session_in_db(budget, uname):
    """
    Updates the field 'tweets_per_session' in the DB.

    Parameters
    ----------
    budget: Number of tweets to be annotated in this session.
    uname: Username of the annotator.

    """
    uname = username_to_mongo(uname)
    Annotator.objects.get(username=uname).update(
        set__tweets_per_session=budget)


def decrement_tweets_to_annotate_in_db(uname):
    """
    Decrements the field 'tweets_to_annotate' in the DB.

    Parameters
    ----------
    uname: User name of the annotator.

    """
    uname = username_to_mongo(uname)
    Annotator.objects.get(username=uname).update(dec__tweets_to_annotate=1)


def update_completed_previous_session_in_db(has_completed, username):
    """
    Updates the field 'completed_previous_session' in DB.

    Parameters
    ----------
    username: Username of the annotator.
    has_completed: Boolean value that should be stored to indicate whether
    annotator has finished or not.

    """
    username = username_to_mongo(username)
    Annotator.objects.get(username=username).update(
         set__completed_previous_session=has_completed)


# def update_index_in_annotated_tweets_in_db(idx, uname):
#     """
#     Updates the field 'index_in_annotated_tweets' in the DB.
#
#     Parameters
#     ----------
#     idx: New index value.
#     uname: User name of the annotator.
#
#     """
#     Annotator.objects.get(username=uname).update(
#         set__index_in_annotated_tweets=idx)


# def get_next_annotated_tweet_from_db(idx, uname):
#     """
#     Finds the tweet that was annotated at position idx by the annotator with
#     the specified username.
#
#     Parameters
#     ----------
#     uname: User name of the annotator.
#
#     Returns
#     -------
#     Tweet object stored at the specified position.
#
#     """
#     return Annotator.objects.get(username=uname)


def update_succ_in_db(succ_id, username, tweet_id):
    """
    Updates the field "succ" in the DB.

    Parameters
    ----------
    succ_id: Tweet ID of successor.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet that will be updated.

    """
    # Tweet.objects.get(id=tweet_id).update(set__succ=succ_id)
    try:
        username = username_to_mongo(username)
        Tweet.objects.get(id=tweet_id).update(
                **{"set__succ__"+username: succ_id})
    except Exception as e:
        print "exception while update_succ_in_db:", e, e.message


def update_pred_in_db(pred_id, username, tweet_id):
    """
    Updates the field "pred" in the DB.

    Parameters
    ----------
    pred_id: Tweet ID of predecessor.
    username: Name of annotator who labeled tweet.
    tweet_id: ID of tweet that will be updated.

    """
    # Tweet.objects.get(id=tweet_id).update(set__pred=pred_id)
    try:
        username = username_to_mongo(username)
        Tweet.objects.get(id=tweet_id).update(
                **{"set__pred__"+username: pred_id})
    except Exception as e:
        print "exception while update_pred_in_db:", e, e.message


# def remove_next_tweet_from_db(uname):
#     """
#     Removes the existing entry in the field 'next_tweet' from the DB
#     indicating that a new one has to be calculated next time.
#
#     Parameters
#     ----------
#     uname: User name of the annotator.
#
#     """
#     Annotator.objects.get(username=uname).update(unset__next_tweet=1)
