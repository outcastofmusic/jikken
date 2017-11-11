def check_mongo(uri=None):
    from pymongo import MongoClient
    from pymongo.errors import ServerSelectionTimeoutError
    uri = "mongodb://localhost:27019" if uri is None else uri
    client = MongoClient(uri, serverSelectionTimeoutMS=300)
    try:
        client.server_info()
        found_database = True
    except ServerSelectionTimeoutError:
        found_database = False
    return found_database
