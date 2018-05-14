from mongoengine import *
from mongoengine.django.auth import User

from TweetLabTool import settings

# class UnlabeledQuerySet(QuerySet):
#     def get_unlabeled_tweets(self):
#         return self.filter(annotation_timestamp__not__ne=None)


class Tweet(Document):
    # see here for explanation of Twitter attributes:
    # https://dev.twitter.com/overview/api/tweets
    # see here for explanation of fields:
    # #http://docs.mongoengine.org/en/latest/guide/defining-documents.html
    text = StringField(max_length=140)
    is_quote_status = BooleanField(default="False")
    retweet_count = IntField()
    quoted_status_id = IntField()
    quoted_status = DictField()
    quoted_status_id_str = StringField(default="null")
    created_at = DateTimeField()
    contributors = DictField()
    truncated = BooleanField()
    in_reply_to_status_id = StringField(default="null")   # Nullable
    favorite_count = IntField()
    source = StringField()
    retweeted = BooleanField()
    coordinates = MultiPointField()
    timestamp_ms = StringField()
    entities = DictField()
    alchemy = DictField()
    in_reply_to_screen_name = StringField()
    id_str = StringField()
    in_reply_to_user_id = StringField(default="null")  # Nullable
    favorited = BooleanField()
    retweeted_status = DictField()
    user = DictField()
    geo = StringField()  # Deprecated and null
    in_reply_to_user_id_str = StringField()
    possibly_sensitive = BooleanField()
    lang = StringField()
    filter_level = StringField()
    in_reply_to_status_id_str = StringField()
    place = DictField()
    extended_entities = DictField()
    # Meta data
    # 1st set of labels
    relevance_label = DictField()
    relevance_time = DictField()
    confidence_relevance = DictField()
    confidence_relevance_time = DictField()
    # 2nd set of labels
    fact_label = DictField()
    fact_time = DictField()
    confidence_fact = DictField()
    confidence_fact_time = DictField()
    # 3rd set of labels
    opinion_label = DictField()
    opinion_time = DictField()
    confidence_opinion = DictField()
    confidence_opinion_time = DictField()
    # When was the annotation submitted the last time?
    #annotation_timestamp = DateTimeField()
    # When did a user submit an annotation for the tweet the last time?
    annotation_timestamp = DictField()
    # Next tweet that was/is going to be annotated
    succ = DictField()
    # Previous tweet that was annotated
    pred = DictField()
    meta = {
        # Use the collection called "tweets" which was created externally
        'collection': settings.TWEET_COLLECTION,
        # Call it like Tweet.objects.get_unlabeled_tweets() to obtain a query
        #  set containing only unlabeled tweets
        # 'queryset_class': UnlabeledQuerySet
    }


class Annotator(User):
    # TODO: don't forget to add a list of sessions where it is stored which
    # tweets that annotator labeled during the session
    # TODO: add choices for different fields, e.g. group -> display in
    # template using https://github.com/jschrewe/django-mongodbforms
    # TODO: http://stackoverflow.com/questions/11923317/creating-django-forms
    # group = StringField(max_length=1, choices=settings.ANNOTATOR_GROUPS,
    #                     required=True)
    # Stores the unhashed password to allow quick password recovery
    # TODO: remove 'raw_password' field and replace it with an recovery
    # system via email
    # email = EmailField(required=True, unique=True)
    username = StringField()
    raw_password = StringField()
    group = StringField(max_length=1, required=True)
    # How many tweets does an annotator have to annotator according to his
    # group policy? -> set according to group affiliation
    tweets_per_session = IntField(max_value=settings.ANNOTATOR_GROUPS["L"])
    # How many tweets has the annotator labeled in this session?
    annotated_in_session = IntField(default=0)
    # #tweets an annotator still has to label according to his/her group
    tweets_to_annotate = IntField()
    # Points to the tweet to be labeled next by the annotator -> updated by
    # AL strategy
    next_tweet = ObjectIdField()
    degree_program = StringField(required=True)
    sex = StringField(max_length=6, required=True)
    nationality = StringField(required=True)
    semesters = IntField(required=True)
    faculty = StringField(required=True)
    level = StringField(required=True)
    # List of tweet IDs that the annotator labeled. This field isn't used
    #  anymore -> DEPRECATED
    annotated_tweets = ListField(ObjectIdField())
    # List of tweet IDs which could be labeled by the annotator
    unlabeled_tweet_ids = ListField(ObjectIdField())
    # In the worst case, all available tweets must be labeled by the annotator
    unlabeled_tweets = IntField(default=0)
    # Total number of tweets in dataset
    total_tweets = IntField(default=0)
    # The position at which the annotator is now in the list of annotated
    # tweets, which might be important when going back and forth in the list
    # using "next" or "previous" on the web page. This index allows to
    # navigate only through all tweets of a session. 1 has to be subtracted to
    #  get the index because it actually represents the number of annotated
    # elements where the last element is yet unlabeled. This field isn't used
    #  anymore -> DEPRECATED
    # index_in_annotated_tweets = IntField()
    # al_strategy = StringField(choices=settings.AL_STRATEGIES.keys(),
    #                           default="RS")
    al_strategy = StringField(required=True, default="RS")
    # Indicates whether annotator
    completed_previous_session = BooleanField(default=False)
    # Allow users to log in again only after a certain amount of time has passed
    # last_login = DateTimeField()
    # List of tweets that were annotated in the previous session -> necessary
    # guarantee that users take a break after finishing their session
    # last_session_annotated_tweets = ListField(ObjectIdField())
    # Flag indicating whether an annotator's account was created manually and
    #  hasn't been registered by the annotator yet. The flag is initially
    # True when the annotator is added manually, but when registering it's
    # set to False
    # is_new = BooleanField(default=False)
