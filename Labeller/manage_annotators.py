import json
import os
import sys

from pymongo import MongoClient
import argparse
from pymongo.errors import DuplicateKeyError
# Script is run outside the project -> make sure it can access its parent dir
sys.path.insert(0, '../')
from TweetLabTool import settings
"""
This file is a script to add a specific user to the MongoDB or remove a
person from it.
"""


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
    # If on Openshift, authenticate to be able to access/edit DBs
    if 'OPENSHIFT_REPO_DIR' in os.environ:
        username = os.environ['OPENSHIFT_MONGODB_DB_USERNAME']
        password = os.environ['OPENSHIFT_MONGODB_DB_PASSWORD']
        client.admin.authenticate(name=username, password=password)
    return client


def get_db(connection, db_name):
    """
    Gets the MongoDB database.

    Parameters
    ----------
    connection: Connection to the database.
    db_name: Name of the MongoDB DB.

    Returns
    -------
    MongoDB database instance.

    """
    # db = connection.annotation_tool
    db = connection[db_name]
    return db


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


def add_annotator(al_strategy, email, group, db_host, db_port,
                  db_name, collection_name):
    """
    Adds an annotator with the specified parameters and default values to
    MongoDB. Sends an info email to the specified email address.

    Parameters
    ----------
    al_strategy: Abbreviation of AL strategy the annotator will be using.
    Values are Uncertainty Sampling: "UC", Random Sampling: "RS", OPAL: "OPAL".
    email: Email address and username of the annotator.
    group: Annotator group determining the number of tweets an annotator has
    to label. Values are "S"mall, "M"edium and "L"arge.
    db_host: Host of DB, e.g. localhost.
    db_port: Port used for communicating with the DB.
    db_name: Name of MongoDB DB.
    collection_name: Name of the collection in which the annotators should be
    stored.

    Raises
    ------
    DuplicateKeyError in case the email (=username) is already stored in the DB.

    """
    conn = get_connection(db_host, db_port)
    my_db = get_db(conn, db_name)
    tweets_per_session = settings.TWEETS_PER_SESSION
    tweets_to_annotate = settings.ANNOTATOR_GROUPS[group]
    print "group:", group
    print "user annotates per session {} tweets".format(tweets_per_session)
    print "user has to annotate {} tweets in total".format(tweets_to_annotate)

    data = {
        "email": email,
        "username": username_to_mongo(email),
        "password": None,
        "al_strategy": al_strategy,
        "group": group,
        "tweets_per_session": tweets_per_session,
        "annotated_in_session": 0,
        "tweets_to_annotate": tweets_to_annotate,
        "next_tweet": None,
        # "degree_program": "a",
        # "sex": "male",
        # "nationality": "a",
        # "semesters": 1,
        # "faculty": "FENS",
        # "level": "BA",
        "annotated_tweets": [],
        "unlabeled_tweets": 0,
        "unlabeled_tweet_ids": [],
        "total_tweets": 0,
        "is_active": True,
        "is_staff": False,
        "is_superuser": False,
        "last_login": None,
        "date_joined": None,
        "user_permissions": None,
        "_cls": "User.Annotator",
    }
    # Try to find the annotator in the DB based on the username (= email
    # address) - if he/she already exists, raise an exception indicating that
    #  this user can't be added. Add the new user otherwise.
    email = username_to_mongo(email)
    user = my_db[collection_name].find_one({"username": email})
    if user is None:
        print "add user", email
        my_db[collection_name].insert(data)
    else:
        raise DuplicateKeyError(email + " already exists as annotator in %s "
                                % my_db[collection_name])


def delete_annotator(email, db_host, db_port,
                     db_name, collection_name):
    """
    Deletes a given annotator (based on email address) from MongoDB. If
    annotator doesn't exist, nothing happens.

    Parameters
    ----------
    email: Email address and username of the annotator.
    db_host: Host of DB, e.g. localhost.
    db_port: Port used for communicating with the DB.
    db_name: Name of MongoDB DB.
    collection_name: Name of the collection in which the annotators should be
    stored.

    """
    conn = get_connection(db_host, db_port)
    my_db = get_db(conn, db_name)
    # Try to find the annotator in the DB based on the username - if he/she
    # already exists, raise an exception indicating that this user can't be
    # added. Add the new user
    my_db[collection_name].remove({"username": username_to_mongo(email)})


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
    print "#############"
    print "# IMPORTANT #"
    print "#############"
    print "TWEET DB MUST EXIST BEFORE THIS SCRIPT IS RUN!"
    parser = argparse.ArgumentParser(description="Add an annotator to MongoDB.")
    parser.add_argument(
        "-ip",
        "--db_host",
        help="Specify the host (default: 'localhost')",
        # Default value if none is specified
        const="localhost",
        # 0 or 1 arguments if parameter is specified without value
        nargs="?",
        # Default value if parameter isn't mentioned at all
        default="localhost"
    )
    parser.add_argument(
        "-p",
        "--db_port",
        help="Specify the port to communicate with the DB (default: 27017).",
        nargs="?",
        const=27017,
        # Convert string automatically to int
        type=int,
        default=27017
    )
    parser.add_argument(
        "-dn",
        "--db_name",
        help="Specify the DB name to which to add the user (default: "
             "annotationtool).",
        default="annotationtool"
    )
    parser.add_argument(
        "-cn",
        "--coll_name",
        help="Specify the name of the collection to which the user will be "
             "added (default: user).",
        default="user"
    )
    parser.add_argument(
        "name",
        help="Username to be added to the DB",
    )
    parser.add_argument(
        "-al",
        "--strategy",
        help="Specify AL strategy. Values are uncertainty sampling 'UC', "
             "random sampling 'RS' and 'OPAL' default('RS').",
        choices=["RS", "UC", "OPAL"],
        default="RS"
    )
    parser.add_argument(
        "-g",
        "--group",
        help="Specify annotator group. Values are (L)arge, (M)edium and ("
             "S)mall default('S').",
        choices=["S", "M", "L"],
        default="S"
    )
    # Make sure user may only invoke delete or add at the same time
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-add",
        "--add",
        # If --add is chosen, it's set to "True" automatically
        action="store_true"
    )
    group.add_argument(
        "-del",
        "--delete",
        action="store_true"
    )
    args = parser.parse_args()

    # Add annotator
    if args.add:
        # print args
        add_annotator(args.strategy, args.name, args.group, args.db_host,
                      args.db_port, args.db_name, args.coll_name)
    if args.delete:
        delete_annotator(args.name, args.db_host, args.db_port, args.db_name,
                         args.coll_name)
    # Examples (local):
    # Add user "stefan@sabanciuniv":
    # python manage_annotators.py stefan@sabanciuniv.edu --add
    # Delete the same user
    # python manage_annotators.py stefan@sabanciuniv.edu --delete

    # Examples (Openshift):
    # go into directory:
    # cd app-root/runtime/repo/Labeller/
    # python manage_annotators.py -p $OPENSHIFT_MONGODB_DB_PORT --db_host $OPENSHIFT_MONGODB_DB_HOST --db_name annotationtool --group M stefan.raebiger@gmail.com --add
    # python manage_annotators.oy -p $OPENSHIFT_MONGODB_DB_PORT --db_host $OPENSHIFT_MONGODB_DB_HOST --db_name annotationtool --delete


    # add_annotator("RS", "stefan@sabanciuniv.edu", "L", DB_HOST, DB_PORT,
    #                       "annotation_tool", "user")
    # delete_annotator("stefan@sabanciuniv.edu", DB_HOST, DB_PORT,
    #                       "annotation_tool", "user")
