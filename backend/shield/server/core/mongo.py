from tornado.options import options
from pymongo import MongoClient

mongo_client_options = {
    'readPreference': 'secondaryPreferred',
    'socketTimeoutMS': 3000,  # 最多等待3s
    'connectTimeoutMS': 100,  # 100ms
    'serverSelectionTimeoutMS': 500,  # 500ms
}

aizhaopin_client = MongoClient(options.AIZHAOPIN_MONGO_SERVER, **mongo_client_options)
aizhaopin_collection = aizhaopin_client[options.AIZHAOPIN_MONGO_DB][options.AIZHAOPIN_MONGO_COLLECTION]
aizhaopin_large_collecion = aizhaopin_client[options.AIZHAOPIN_MONGO_DB][options.AIZHAOPIN_MONGO_COLLECTION_LARGE]
