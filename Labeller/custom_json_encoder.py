"""
This encoder allows to serialize Object IDs from MongoDB into JSON.
"""
from json import JSONEncoder
from bson.objectid import ObjectId


class MongoEncoder(JSONEncoder):
    def default(self, obj, **kwargs):
        if isinstance(obj, ObjectId):
            return str(obj)
        else:            
            return JSONEncoder.default(obj, **kwargs)
