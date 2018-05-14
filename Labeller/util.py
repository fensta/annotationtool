"""
Contains some utility functions
"""
import random
import time
import json
import datetime

from TweetLabTool import settings
from django.http import JsonResponse

from Labeller.custom_json_encoder import MongoEncoder
from Labeller.db_queries import *


def extract_data_from_registration(data, fields, mapping):
    """
    Extract the necessary information from the POST request.

    Parameters
    ----------
    fields: List of keys that have to be present in the request.
    data: Data from the request.
    mapping: Dictionary assigning each field key the textual representation
    that should be shown to the annotator.

    Returns
    -------
    Boolean, dict, string
    True, if all fields could be extracted. Otherwise False.
    The dict contains the extracted values for each single key that was
    extracted successfully from the request, e.g. {field1: val1, field2: val2}.
    The string contains the missing fields that are displayed to the annotator.

    """
    missing = ""
    is_valid = True
    vals = {}
    for entry in fields:
        # Field not empty and it exists in request -> it's valid
        if entry in data and not data[entry] == "":
            vals[entry] = data.get(entry)
        else:
            is_valid = False
            missing += mapping[entry]
    return is_valid, vals, missing


def random_sampling(budget, anno):
    """
    Simulates the active learning strategy random sampling for selecting a
    tweet to be labeled.

    Parameters
    ----------
    data: Entire dataset from the DB to be used for active learning.
    budget: Number of tweets to be annotated in this session.
    anno: Annotator object from DB who is going to annotate the tweet.

    Returns
    -------
    Tweet object to get annotated next. It returns None if no more unlabeled
    tweets exist.

    """
    # print "+++++++++++++++"
    # print "Random Sampling"
    # print "+++++++++++++++"
    # try:
    #     # b = Tweet.objects()
    #     # print "b", b
    #     tweets = Tweet.objects()
    #     for t in tweets:
    #         print t.text
    # except Exception as e:
    #     print "tweet all() exceptions:", e, e.message
    # print "unlabeled tweets:", unlabeled_tweets, len(unlabeled_tweets)
    # try:
    #     for t in unlabeled_tweets:
    #         text = t.text.encode("utf-8")
    #         print text
    # except Exception as e:
    #     print str(e)
    # 2nd criterion was already checked in function invoking random_sampling,
    # but let's be safe
    if anno.unlabeled_tweets == 0 or budget == 0:
        return None
    # test = Tweet.objects.get_unlabeled_tweets()
    # print "unlabeled alternative:"
    # for t in test:
    #     print t.text
    # Get all tweets whose annotation_timestamp is empty
    # print "random number between 0 and", anno.unlabeled_tweets - 1
    try:
        tweet_idx = random.randint(0, anno.unlabeled_tweets - 1)
    except ValueError:
        return None
    # print "random number:", tweet_idx
    # data = list(unlabeled_tweets)
    unlabeled_tweet_id = anno.unlabeled_tweet_ids[tweet_idx]
    unlabeled_tweet = get_tweet_from_db(unlabeled_tweet_id)
    # print unlabeled_tweet._data
    # Reveal the next tweet to be labeled to the annotator
    return unlabeled_tweet


def uncertainty_sampling(data, budget, anno):
    """
    Simulates the active learning strategy uncertainty sampling for selecting a
    tweet to be labeled.

    Parameters
    ----------
    data: Entire dataset from the DB to be used for active learning.
    budget: Number of tweets to be annotated in this session.
    anno: Annotator object from DB who is going to annotate the tweet.

    """
    return None


def determine_next_tweet_by_AL(anno):
    """
    Finds the next tweet to be annotated by the annotator.

    Parameters
    ----------
    anno: Annotator object - represents the current annotator.

    Returns
    -------
    Tweet object to be annotated. Returns None if the budget is exhausted or the
    DB is empty, annotator has completed the job. It returns "error" if the
    budget is negative. It returns "session completed" if an annotator
    labeled all tweets in the current session, but some tweets need to be
    labeled in later sessions.

    """
    # print "+++++++++++++++++++++++++++++++++++++++"
    # print "determine_next_tweet_by_AL()"
    # print "+++++++++++++++++++++++++++++++++++++++"
    # Without [0] it's a queryset with 1 tweet, but we only want the tweet
    # anno = get_annotator_from_db(username)
    # print "current annotator:", anno
    # #Tweets left to annotate
    strategy = anno.al_strategy
    # budget = get_budget(anno)
    budget = get_number_of_tweets_to_be_labeled_in_session(anno)
    # if budget == settings.ERRORS["InvalidBudget"]:
    #     raise Exception(budget)
    # print "annotated in session so far:", anno.annotated_in_session
    # print "budget:", get_number_of_tweets_to_be_labeled_in_session(anno)
    # print "annotate another tweet?", budget > 0
    # if anno.annotated_in_session < \
    #         get_number_of_tweets_to_be_labeled_in_session(anno):
    if budget > 0:
        # update_tweets_per_session_in_db(budget, username)
        # dataset = list(Tweet.objects.all())
        # TODO: Can this part be automated so that only the strategies are
        # specified in the settings file?
        if strategy == "RS":
            tweet = random_sampling(budget, anno)
        # if strategy == "US":
        #     tweet = uncertainty_sampling(dataset, budget, anno)
        # Unlabeled tweets are available in DB
        if tweet is not None:
            update_next_tweet_in_db(tweet.id, anno.username)
            # annotated_tweets = list(anno.annotated_tweets)
            if len(anno.annotated_tweets) > 0:
                # print "+++++++++++++++++++++++++++++++++++++++++"
                # print "+++++++ update doubly linked list +++++++"
                last_tweet_id = anno.annotated_tweets[-1:][0]
                update_succ_in_db(tweet.id, anno.username, last_tweet_id)
                update_pred_in_db(last_tweet_id, anno.username, tweet.id)
            return tweet
        else:
            return "session completed"
    elif budget == 0:
        return None
    else:
        # raise Exception("Budget is negative!")
        return "error"


def to_dict(data):
    """
    Converts jQuery object into a Python dictionary and returns it.

    Parameters
    ----------
    data: jQuery object.

    Returns
    -------
    Python dictionary, message including the error. If no error occurs,
    this message is empty.

    """
    converted = {}
    msg = ""
    try:
        converted = json.loads(data)
    except Exception as e:
        msg += "POST request isn't a JSON object and couldn't be converted " \
               "into a Python dictionary!"
        msg += e.message
    return converted, msg


def annotate_tweet(tweet, anno, data, fields):
    """
    Adds the annotation data from the annotator to the tweet in the DB.

    Parameters
    ----------
    tweet: Tweet object that was annotated.
    anno: Annotator object that annotated the tweet.
    data: Data received from annotator.
    fields: Mapping of fields from received data to DB fields. (Not used as
    of now, but might become useful).

    Returns
    -------
    boolean.
    True if received data was valid and stored in DB, False otherwise.

    """
    # print "{} has annotated {} - store that in DB!".format(anno.username,
    #                                                        tweet.id)
    # If a time isn't present, assume it's 0
    # Relevance label
    rel_label = data.get("relevance", None)
    # Time needed for assigning label
    rel_time = data.get("relevance_time", 0)
    # Confidence label for relevance
    rel_conf_label = data.get("confidence_relevance", None)
    # Time required to assign confidence label for relevance
    rel_conf_time = data.get("confidence_relevance_time", 0)
    # Factual label
    fac_label = data.get("fact", None)
    # Time needed for assigning label
    fac_time = data.get("fact_time", 0)
    # Confidence label for relevance
    fac_conf_label = data.get("confidence_fact", None)
    # Time required to assign confidence label for relevance
    fac_conf_time = data.get("confidence_fact_time", 0)
    # Opinion label
    opi_label = data.get("opinion", None)
    # Time needed for assigning label
    opi_time = data.get("opinion_time", 0)
    # Confidence label for opinion
    opi_conf_label = data.get("confidence_opinion", None)
    # Time required to assign confidence label for opinion
    opi_conf_time = data.get("confidence_opinion_time", 0)
    # Timestamp when the tweet was submitted by the annotator
    anno_timestamp = data.get("annotation_timestamp", None)
    is_valid = False
    # If any of the measured times is negative, invalidate whole tweet and
    # prompt user to logout and login again to repeat this annotation

    # Check 1st and 2nd set of labels first since they always exist
    if rel_time > 0 and fac_time > 0 and rel_conf_time > 0 \
            and fac_conf_time > 0:
        is_valid = True
    # If annotator also used 3rd set of labels, check it as well - it's valid
    # if sets 1 and 2 are valid and set 3 is valid itself
    if opi_label is not None and is_valid and opi_time > 0 \
            and opi_conf_time > 0:
        is_valid = True
    if not is_valid:
        return False

    # Store 1st set of labels
    update_relevance_label_in_db(rel_label, anno.username, tweet.id)
    update_relevance_time_in_db(rel_time, anno.username, tweet.id)
    update_relevance_confidence_in_db(rel_conf_label, anno.username, tweet.id)
    update_relevance_confidence_time_in_db(rel_conf_time, anno.username,
                                           tweet.id)
    # print "relevance label", rel_label
    # print "relevance time", rel_time
    # print "confidence label", rel_conf_label
    # print "confidence time", rel_conf_time
    # Store timestamp
    # Time stamp in UTC format instead of local time
    # it looks like this currently: Sat, 27 Jun 2015 22:58:19 GMT
    d = datetime.datetime.strptime(anno_timestamp, "%a, %d %b %Y %H:%M:%S %Z")
    # TODO: is conversion of timestamp into local time zone necessary? then
    # comment out the next part
    # print "date utc", d
    # from dateutil import tz
    # from_zone = tz.tzutc()
    # to_zone = tz.tzlocal()
    # utc = d.replace(tzinfo=from_zone)
    # # Convert time zone
    # d = utc.astimezone(to_zone)
    # print "local time", d

    # Update list of annotated tweets and indices only if the tweet is newly
    # labeled. This can be determined by checking whether an annotation
    # timestamp exists. Only if it doesn't exist, update the DB
    # print "who's stored in annotation timestamp so far?", \
    #     tweet.annotation_timestamp
    user_annotated_tweet_before = anno.username in tweet.annotation_timestamp
    # print "add tweet to annotated tweets of user?", \
    #     not user_annotated_tweet_before
    update_annotation_timestamp_in_db(tweet.id, anno.username, d)
    # Store the 2nd set of labels
    # print "2nd set of labels was also used by annotator!"
    update_fact_label_in_db(fac_label, anno.username, tweet.id)
    update_fact_time_in_db(fac_time, anno.username, tweet.id)
    update_fact_confidence_in_db(fac_conf_label, anno.username, tweet.id)
    update_fact_confidence_time_in_db(fac_conf_time, anno.username, tweet.id)
    # print "fact label", fac_label
    # print "fact time", fac_time
    # print "confidence label", fac_conf_label
    # print "confidence time", fac_conf_time
    # Store 3rd set of labels if annotator assigned them
    # if fac_label == "Non-factual":

    # If user relabels tweet, he/she might choose "Factual" now (initially it
    # was "non-factual"). Hence, the server will send negative times for the
    # 3rd set of labels (end time - start time, where end time is 0 since
    # the timer never started as the 3rd set of labels is hidden and start
    # time is a positive value)
    if user_annotated_tweet_before:
        # print "user is reannotating tweet", tweet.id
        # User annotated tweet earlier
        if opi_label is None:
            # print "user has changed opinion and now selected 'Factual'"
            # print "3rd set of labels was perhaps chosen in previous " \
            #       "annotation by annotator but now it's not used anymore"
            # Time could be negative if user deselected 3rd set of labels: then
            # update all labels to None
            # if opi_time < 0:
            #     opi_time = None
            # if opi_conf_time < 0:
            #     opi_conf_time = None
            # DON'T remove the annotation times as they still contributed to the
            # total annotation time! Indicate that the 3rd set of labels wasn't
            # used by simply removing the labels, but retain the times!!!
            if anno.username in tweet.opinion_label:
                label_to_be_removed = tweet.opinion_label[anno.username]
                remove_opinion_label_in_db(label_to_be_removed, anno.username,
                                           tweet.id)

            # if anno.username in tweet.opinion_time:
            #     time_to_be_removed = tweet.opinion_time[anno.username]
            #     remove_opinion_time_in_db(time_to_be_removed, anno.username,
            #                               tweet.id)

            if anno.username in tweet.confidence_opinion:
                confidence_to_be_removed = tweet.confidence_opinion[anno.username]
                remove_opinion_confidence_in_db(confidence_to_be_removed,
                                                anno.username, tweet.id)

            # if anno.username in tweet.confidence_opinion_time:
            #     confidence_time_to_be_removed = tweet.confidence_opinion_time[
            #         anno.username]
            #     remove_opinion_confidence_time_in_db(
            #         confidence_time_to_be_removed, anno.username, tweet.id)
            # print "opinion label", opi_label
            # print "opinion time", opi_time
            # print "confidence label", opi_conf_label
            # print "confidence time", opi_conf_time
        else:
            # Update 3rd set of labels
            print "ok, user reannotates tweet and used 3rd set of labels -> " \
                  "update"
            update_opinion_label_in_db(opi_label, anno.username, tweet.id)
            update_opinion_time_in_db(opi_time, anno.username, tweet.id)
            update_opinion_confidence_in_db(opi_conf_label, anno.username,
                                            tweet.id)
            update_opinion_confidence_time_in_db(opi_conf_time, anno.username,
                                                 tweet.id)
            # print "updated 3rd set of labels successfully"
    else:
        # User annotated for the first time -> only if he/she selected 3rd
        # set of labels, update it
        if fac_label == "Non-factual":
            update_opinion_label_in_db(opi_label, anno.username, tweet.id)
            update_opinion_time_in_db(opi_time, anno.username, tweet.id)
            update_opinion_confidence_in_db(opi_conf_label, anno.username,
                                            tweet.id)
            update_opinion_confidence_time_in_db(opi_conf_time,
                                                 anno.username, tweet.id)
            # For the commented part it's necessary to reload the tweet!
            # if anno.username in tweet.opinion_label:
            #     print "opinion label", tweet.opinion_label[anno.username]
            # print "opinion time", tweet.opinion_time[anno.username]
            # if anno.username in tweet.confidence_opinion:
            #     print "confidence label", tweet.confidence_opinion[
            #         anno.username]
            # print "confidence time", tweet.confidence_opinion_time[
            #     anno.username]
            print "stored 3rd set of labels successfully"
    # If user annotated tweet for the 1st time, update the progress
    if not user_annotated_tweet_before:
        # print "annotator {} has labeled tweet {} for the first time! u" \
        #       "pdate statistics...".format(anno.username, tweet.id)
        # Add labels to annotator
        # annotated_in_session = anno.annotated_in_session
        increment_annotated_in_session_in_db(anno.username)
        # Reduce number of tweets to be annotated by 1
        decrement_tweets_to_annotate_in_db(anno.username)
        # Store that annotator labeled this tweet
        update_annotated_tweets_in_db(tweet.id, anno.username)
        update_unlabeled_tweets_in_db(tweet.id, anno.username)
        # Delete the currently labeled tweet from "next_tweet" field
        # This is useful if user presses "enter" to reload page, so the same
        # tweet won't be reloaded
        update_next_tweet_in_db(None, anno.username)
        # Update unlabeled tweets
        update_unlabeled_tweets_in_db(tweet.id, anno.username)
        decrement_unlabeled_tweets_in_db(anno.username)
    return True


def get_budget(anno):
    """
    Finds the available budget of an annotator.

    Parameters
    ----------
    anno: Annotator object.

    Returns
    -------
    Available budget of an annotator.
    If the budget is negative however, budget returns the error message.

    """
    no_tweets = anno.tweets_to_annotate
    budget = settings.ERRORS["InvalidBudget"]
    group = anno.group
    if group in settings.ANNOTATOR_GROUPS:
        # print "tweets to label per session", settings.TWEETS_PER_SESSION
        # In "L" users can annotate 500 tweets at a time convenient for them
        if group != "L":
            # print "group other than 'L'"
            if no_tweets > settings.TWEETS_PER_SESSION:
                # print "currently already labeled", no_tweets
                # if no_tweets > settings.TWEETS_PER_SESSION:
                # print "too many remaining tweets, label only", \
                #     settings.TWEETS_PER_SESSION
                # More than TWEETS_PER_SESSION tweets are left for annotation
                budget = settings.TWEETS_PER_SESSION
            else:
                # Annotate all remaining tweets which are less than
                # TWEETS_PER_SESSION
                # print "let's finish annotating the remaining", no_tweets
                budget = no_tweets
        else:
            # print "'L' is labeled"
            if no_tweets > settings.TWEET_LIMIT:
                # print "user has to label", settings.TWEETS_PER_SESSION
                budget = settings.TWEETS_PER_SESSION
            else:
                # print "user is free to label the remaining", no_tweets
                budget = no_tweets
        # print "{} belonging to {} has to annotate {} tweets in this " \
        #       "session".format(anno.username, group, budget)
    # print "currently annotated tweets by anno:", len(anno.annotated_tweets)
    # print "how many should be annotated by his group?", settings.ANNOTATOR_GROUPS[anno.group]
    if len(anno.annotated_tweets) >= settings.ANNOTATOR_GROUPS[anno.group]:
        # print "budget = 0 because anno is done!!!!"
        budget = 0
    return budget


def load_next_tweet(anno, tweet_id):
    """
    Loads the next annotated tweet by the annotator.

    Parameters
    ----------
    anno: Annotator object representing current annotator.
    tweet_id: ID of current tweet

    Returns
    -------
    Dictionary with all the necessary data to update the client. In case
    there is no next tweet, an empty dictionary is returned.

    """
    has_next = False
    # anno = get_annotator_from_db(username)
    tweet = get_tweet_from_db(tweet_id)
    # print "current tweet {} for which successor is requested".format(tweet.id)
    if anno.username in tweet.succ:
        # print "successor:", tweet.succ[anno.username]
        succ_tweet = get_tweet_from_db(tweet.succ[anno.username])
        # print "successor:", succ_tweet.id
        # Successor of successor exists
        if anno.username in succ_tweet.succ:
            has_next = True
        c = add_full_tweet_to_response(succ_tweet, anno,
                                       has_next=has_next)
        return c
    return {}


def load_previous_tweet(username, tweet_id):
    """
    Loads the previously annotated tweet by the annotator.

    Parameters
    ----------
    username: User name of annotator.
    tweet_id: Tweet ID of currently displayed tweet

    Returns
    -------
    Dictionary with all the necessary data to update the client. In case
    there is no previous tweet, an empty dictionary is returned.

    """
    has_previous = False
    anno = get_annotator_from_db(username)
    if len(tweet_id) == 0:    # Annotation completed message is shown
        print "anno wants previous tweet after anno completed annotation"
        # Get last tweet from DB
        annotated_tweets = list(anno.annotated_tweets)
        # print "#labeled tweets in db", len(annotated_tweets)
        if len(annotated_tweets) > 0:
            last_tweet_id = annotated_tweets[-1:][0]
            last_tweet = get_tweet_from_db(last_tweet_id)
            if last_tweet is not None:
                # print "last tweet:", last_tweet.id
                if anno.username in last_tweet.pred:
                    print "predecessor of previous tweet exists"
                    has_previous = True
                c = add_full_tweet_to_response(last_tweet, anno,
                                               has_previous=has_previous)
                # print "full data to be send to client:", c
                return c
            else:
                return {}
    else:
        # print "anno wants previous tweet before anno completed annotation"
        tweet = get_tweet_from_db(tweet_id)
        # print "current tweet:", tweet.id
        # if tweet.pred is not None:
        # print "predecessor: {}".format(tweet.pred.get(anno.username, None))
        if anno.username in tweet.pred:
            prev_tweet = get_tweet_from_db(tweet.pred[anno.username])
            if prev_tweet is not None:
                # print "previous tweet:", prev_tweet.id

                # print "previously annotated tweet:", tweet.pred
                # Predecessor of predecessor exists
                if anno.username in prev_tweet.pred:
                    # print "predecessor of previous tweet exists"
                    has_previous = True
                c = add_full_tweet_to_response(prev_tweet, anno,
                                               has_previous=has_previous)
                # print "full data to be send to client:", c
                return c
            return {}
    return {}


def get_last_annotated_tweet_id(annotated_tweets):
    """
    Returns the last annotated tweet ID.

    Parameters
    ----------
    List of annotated tweets by annotator.

    Returns
    -------
    Tweet ID of latest annotated tweet.

    """
    last_annotated_tweet_id = None
    # In the 1st ever run this will be empty, so we need to check
    if len(annotated_tweets) > 0:
        last_annotated_tweet_id = annotated_tweets[-1:][0]
    return last_annotated_tweet_id


def get_next_annotated_tweet_to_be_shown(anno, tweet_id=None):
    """
    Finds the next tweet to be shown to the annotator. This function only
    considers the existing tweets that were already assigned to the annotator.

    Parameters
    ----------
    anno: Annotator object from MongoDB representing the current annotator.

    Returns
    -------
    Tweet, boolean.
    Tweet to be shown to the annotator next. Returns None if there is no
    further assigned tweet available for the annotator, meaning the AL
    strategy has to find one. The function also returns True, if the tweet
    has a successor or not, indicating whether the user can press "next" or not.

    """
    # print "+++++++++++++++++++++++++++++++++++++++"
    # print "get_next_annotated_tweet_to_be_shown()"
    # print "+++++++++++++++++++++++++++++++++++++++"
    # Start view, i.e. figure out which tweet to choose: next_tweet or let AL
    #  strategy choose?
    has_next = False
    # anno = get_annotator_from_db(username)
    # annotated_tweets = list(anno.annotated_tweets)
    # First time this method is called -> let AL strategy choose a new tweet
    if tweet_id is None:
        # Pick either next_tweet or let AL choose
        if anno.next_tweet is not None:
            # See if next_tweet is identical with the last labeled tweet
            last_annotated_tweet_id = get_last_annotated_tweet_id(
                anno.annotated_tweets)
            # Both are identical -> let AL strategy choose the next one
            if last_annotated_tweet_id == anno.next_tweet:
                # print "last tweet == next tweet -> AL"
                return None, has_next
            else:
                # next_tweet hasn't been labeled yet
                # print "last tweet != next tweet -> annotate", anno.next_tweet
                return get_tweet_from_db(anno.next_tweet), has_next
        return None, has_next
    else:
        # Annotator has reannotated a tweet or clicked on "next"/"previous"
        tweet = get_tweet_from_db(tweet_id)
        # Next tweet exists
        if tweet.succ is not None:
            # print "succ for {} exists -> display".format(tweet.succ)
            next_tweet = get_tweet_from_db(tweet.succ)
            # Next tweet also has a successor -> can be browsed by client
            if next_tweet.succ is not None:
                has_next = True
                # print "succ of succ ={} exists".format(next_tweet.succ)
            return next_tweet, has_next
        else:
            # print "label next_tweet? or let AL choose?"
            # Tweet is the last labeled one
            # See if next_tweet is identical with the last labeled tweet
            last_annotated_tweet_id = get_last_annotated_tweet_id(
                anno.annotated_tweets)
            if last_annotated_tweet_id == anno.next_tweet:
                # print "last tweet == next tweet -> AL"
                return None, has_next
            else:
                # next_tweet hasn't been labeled yet
                # print "last tweet != next tweet -> annotate", anno.next_tweet
                return get_tweet_from_db(anno.next_tweet), has_next
    return None, has_next


def add_tweet_to_response(tweet, anno, has_next=None, has_previous=None):
    """
    Adds the necessary data to the JSON response from the server to the client.

    Parameters
    ----------
    tweet: Tweet object.
    anno: Annotator object.
    has_next: True if you can click on next to browse through annotated tweets.
    has_previous: Same as has_next, but for previous tweets.

    Returns
    -------
    Dictionary containing all necessary information for the client.

    """
    h = len(list(anno.annotated_tweets))
    k = anno.annotated_in_session
    # Only if it's not set by other method
    if has_next is None:
        # If tweet ID is different from the next tweet to be labeled, there's a
        # successor
        has_next = False if tweet.id == anno.next_tweet else True

    # print "has_next?", has_next, tweet.id, anno.next_tweet, tweet.id == \
    #       anno.next_tweet
    if has_previous is None:
        has_previous = True if k > 0 else False
    # print "has_previous?", has_previous, k
    # print "total #tweets in session: ", \
        get_number_of_tweets_to_be_labeled_in_session(anno)
    c = {'tweet': tweet.text,
         "total_prog": settings.ANNOTATOR_GROUPS[anno.group],
         "current_prog": h,
         "total_sess": get_number_of_tweets_to_be_labeled_in_session(anno),
         "current_sess": k,
         "tweet_id": tweet.id,
         "has_next": has_next,
         "has_previous": has_previous,
         "username": username_to_email(anno.username)
         }
    return c


def is_tweet_labeled(tweet):
    """
    Checks whether a given tweet was already annotated or not by an annotator.

    Parameters
    ----------
    tweet: Tweet object.

    Returns
    -------
    True, if tweet contains an annotation time stamp, meaning the tweet was
    labeled earlier. Otherwise False is returned.

    """
    # If a tweet was already labeled by annotator (for his/her 1st ever tweet
    #  it will be empty)
    if tweet is not None:
        if tweet.annotation_timestamp is None:
            return False
    return True


def add_full_tweet_to_response(tweet, anno, has_next=False, has_previous=False):
    """
    Fetches all necessary information for client from the DB.

    Parameters
    ----------
    tweet: Tweet object.
    Anno: Annotator object.
    has_next: True if you can click on next to browse through annotated tweets.
    has_previous: Same as has_next, but for previous tweets.

    Returns
    -------
    Dictionary containing all information from the DB.

    """
    c = {}
    # Add the metadata from the annotation that are visible on the client's side
    # print "relevance label in DB?", anno.username in tweet.relevance_label
    if anno.username in tweet.relevance_label:
        # print "tweet {} has relevance data".format(tweet.id)
        c["relevance_label"] = tweet.relevance_label[anno.username]
        c["relevance_time"] = tweet.relevance_time[anno.username]
        c["confidence_relevance_time"] = tweet.confidence_relevance_time[
            anno.username]
        c["confidence_relevance"] = tweet.confidence_relevance[anno.username]
    else:
        # Can happen if annotator labeled tweet 1, tweet 2 was shown. Anno
        # clicks "previous", then "next" and tweet 2 has no labels yet -> then
        # the times would be "None"
        c["relevance_time"] = 0
        c["confidence_relevance_time"] = 0
    # print "fact label in DB?", anno.username in tweet.fact_label
    # if tweet.fact_label is not None:
    if anno.username in tweet.fact_label:
        # print "tweet {} has fact data".format(tweet.id)
        c["fact_label"] = tweet.fact_label[anno.username]
        c["fact_time"] = tweet.fact_time[anno.username]
        c["confidence_fact_time"] = tweet.confidence_fact_time[anno.username]
        c["confidence_fact"] = tweet.confidence_fact[anno.username]
    else:
        # Can happen if annotator labeled tweet 1, tweet 2 was shown. Anno
        # clicks "previous", then "next" and tweet 2 has no labels yet -> then
        # the times would be "None"
        c["fact_time"] = 0
        c["confidence_fact_time"] = 0
    # print "opinion label in DB?", anno.username in tweet.opinion_label
    if anno.username in tweet.opinion_label:
        # print "tweet {} has opinion data".format(tweet.id)
        c["opinion_label"] = tweet.opinion_label[anno.username]
        c["opinion_time"] = tweet.opinion_time[anno.username]
        c["confidence_opinion_time"] = tweet.confidence_opinion_time[
            anno.username]
        c["confidence_opinion"] = tweet.confidence_opinion[anno.username]
    else:
        # Can happen if annotator labeled tweet 1, tweet 2 was shown. Anno
        # clicks "previous", then "next" and tweet 2 has no labels yet -> then
        # the times would be "None"
        c["opinion_time"] = 0
        c["confidence_opinion_time"] = 0
    # Add the standard data
    c.update(add_tweet_to_response(tweet, anno, has_previous=has_previous,
                                   has_next=has_next))
    return c


def determine_next_tweet(anno, tweet_id=None):
    """
    Determines the next tweet to be annotated. It could be either simply the
    next tweet a user already annotated earlier, if he/she just reannotated
    another tweet. Or the AL strategy has to choose the next tweet. Or the user
    already labeled all tweets.

    Parameters
    ----------
    anno: Annotator object representing the current annotator.

    Returns
    -------
    Tweet object. It returns None in case no tweet in the DB is left to
    annotate or the session is over or a user already labeled all tweets in
    previous sessions. In case of a negative budget, it returns "error".

    """
    # anno = get_annotator_from_db(username)
    # Start view - figure out which one is next: next_tweet from DB, the last
    #  annotated one
    # annotated_tweets = len(list(anno.annotated_tweets))
    # if anno.index_in_annotated_tweets < annotated_tweets:
    # print "+++++++++++++++++++++"
    # print "determine_next_tweet()"
    # print "+++++++++++++++++++++"
    tweet = get_next_annotated_tweet_to_be_shown(anno, tweet_id)[0]
    # print "currently annotated tweets by anno:", len(anno.annotated_tweets)
    # print "how many should be annotated by his group?", \
    #     settings.ANNOTATOR_GROUPS[anno.group]
    # a) User reannotated tweet -> load the next one he/she annotated
    if tweet is not None:
        # print tweet
        print "Show next tweet with ID: ", tweet.id
        # print "---------------------------"
    # b) Annotation was finished in earlier session
    elif len(anno.annotated_tweets) >= settings.ANNOTATOR_GROUPS[anno.group]:
        return None
    # c) Let AL strategy determine next tweet
    else:
        # print "determine next tweet for annotation by AL"
        # print "-----------------------------------"
        tweet = determine_next_tweet_by_AL(anno)
        if tweet == "error":
            return "error"
    return tweet


def annotation_completed(anno, can_continue=False):
    """
    Function sends the respective information to the client that he/she has
    completed the session and may log out now.

    Parameters
    ----------
    anno: Annotator object who completed the session.
    can_continue: True if annotator can continue labeling after logout. This
    can only occur for annotators of group "L" when the session conflicts
    with TWEET_LIMIT.

    Returns
    -------
    A message for the user and proper information for the client GUI.

    """
    update_completed_previous_session_in_db(True, anno.username)
    # Session completed by annotator
    h = len(list(anno.annotated_tweets))
    k = anno.annotated_in_session
    username = username_to_email(anno.username)
    username = username.split("@")[0]
    msg = "Annotation finished. Please, log out."
    c = {'tweet': msg,
         "total_prog":  settings.ANNOTATOR_GROUPS[
             anno.group],
         "current_prog": h,
         "total_sess": anno.tweets_per_session,
         "current_sess": k,
         "tweet_id": None,
         "has_next": False,
         "has_previous": True,
         "username": username,
         "SESSION_FINISHED": "You have finished your "
                             "session. Thank you a lot "
                             "for your contribution!",
         # "completed_url": url_
         }
    # Session isn't really over, but user has only TWEET_LIMIT tweets left
    # for labeling
    if can_continue:
        c.update({"can_continue": True})
        # update_completed_previous_session_in_db(False, anno.username)
    # else:
        # Session is really over

    return JsonResponse(c, encoder=MongoEncoder)


def compute_waiting_time(anno):
    """
    Computes for how many more minutes an annotator needs to wait before
    he/she may log in again to continue labeling the next bulk of tweets.

    Parameters
    ----------
    anno: Annotator object.

    Returns
    -------
    Boolean, int.
    True/False whether login is allowed at the moment and the time to wait in
    minutes. 0 indicates that annotators are free to start their next session.
    Returns True if login is NOT allowed.

    """
    to_wait = False
    anno_username = anno.username.encode("utf-8")
    print "last login by {}: {}".format(anno_username,
                                        anno.last_login)
    # Use UTC because dates are also stored in UTC
    d1 = anno.last_login
    d2 = datetime.datetime.utcnow()
    print "current time: ", d2
    # print "user has waited for {} minutes".format(d2 - d1)
    # Convert to unix timestamp
    d1_ts = time.mktime(d1.timetuple())
    d2_ts = time.mktime(d2.timetuple())
    # They are now in seconds, subtract and then divide by 60 to get minutes.
    waiting_time = int(d2_ts-d1_ts) / 60
    # Now compare it with the threshold
    waiting_time = settings.SESSION_PAUSE - waiting_time
    if waiting_time > 0:
        to_wait = True
    # Consider the case when "L" is free to label the remaining TWEET_LIMIT
    # tweets at their own convenience and pace
    if anno.group == "L":
        if anno.tweets_to_annotate - 1 < settings.TWEET_LIMIT:
            to_wait = False
    print "to_wait?", to_wait
    try:
        # Is annotator allowed to label more tweets in this session?
        # start = time.time()
        unlabeled_tweets = anno.unlabeled_tweets
        # end = time.time()
        # print "time to count unlabeled tweets", (end - start)

        # Yes, if annotator didn't complete previous session and
        # there are some unlabeled tweets available
        print "unlabeled tweets: ", unlabeled_tweets
        print "completed previous session?", anno.completed_previous_session
        if not anno.completed_previous_session and unlabeled_tweets >= 0:
            to_wait = False
        print "Does annotator {} have to wait? {}. Annotator {} has to wait " \
              "{} more minutes before being allowed to log in again!".\
            format(anno_username, to_wait, anno_username, waiting_time)
    except Exception, e:
        print "Error in computing waiting time", e
        print str(e)
    return to_wait, waiting_time


def get_number_of_tweets_to_be_labeled_in_session(anno):
    """
    Finds how many tweets an annotator needs to label in the current session.

    Parameters
    ----------
    anno: Annotator object.

    Returns
    -------
    int.
    Tweets to be labeled in session.

    """
    # How many tweets to annotate in this session?
    # The minimum of:
    # - maximum number of tweets to be labeled per session
    # - remaining tweets to be annotated in this session
    # - overall remaining tweets + annotated tweets in this session so far
    # - for large annotator group L: if more than 500 tweets were already
    #   labeled, the remaining ones are: number of tweets in large group -
    #   labeled tweets
    # Remaining tweets if <= TWEETS_PER_SESSION tweets must be labeled
    remaining_tweets_in_session_1 = settings.ANNOTATOR_GROUPS[anno.group] - \
                                  anno.annotated_in_session
    # Remaining tweets if > TWEETS_PER_SESSION tweets must be labeled
    remaining_tweets_in_session_2 = settings.TWEETS_PER_SESSION - \
                                  anno.annotated_in_session
    total_tweets = settings.ANNOTATOR_GROUPS[anno.group]
    unlabeled_tweets = anno.unlabeled_tweets
    # print "pick minimum:", settings.TWEETS_PER_SESSION, \
    #     remaining_tweets_in_session_1, remaining_tweets_in_session_2, \
    #     unlabeled_tweets + anno.annotated_in_session, total_tweets,\
    #     anno.total_tweets
    max_session = min(
        # Maximum number of tweets to be annotated per session
        settings.TWEETS_PER_SESSION,
        # Tweets left in session to be annotated
        remaining_tweets_in_session_1,
        remaining_tweets_in_session_2,
        unlabeled_tweets + anno.annotated_in_session,
        # Total tweets to be annotated by annotator
        total_tweets,
        # All tweets in DB
        anno.total_tweets
    )
    # If annotator is part of large group
    if anno.group == "L":
        # print "to annotate:", anno.tweets_to_annotate
        # print "TWEET_LIMIT", settings.TWEET_LIMIT - 1
        # And he/she already annotated more than specified threshold in sessions
        # allow him/her to annotate the rest in one go. - 1 because the
        # condition wouldn't hold for the 1st tweet of TWEET_LIMIT as both
        # values would be equal
        if anno.tweets_to_annotate - 1 < settings.TWEET_LIMIT:
            print "ANNOTATOR CAN LABEL PRIVATELY"
            max_session = settings.ANNOTATOR_GROUPS[anno.group] - \
                          len(anno.annotated_tweets)
        else:
            # Reduce number of tweets to be labeled in the session
            # print "remaining L tweets",
            # anno.tweets_to_annotate - settings.TWEET_LIMIT
            max_session = min(max_session, anno.tweets_to_annotate -
                              settings.TWEET_LIMIT)
    # print "remaining tweets to annotate for {} in session: {}". \
    #     format(anno.username, max_session)
    return max_session



