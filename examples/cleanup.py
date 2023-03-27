import pymongo

db = pymongo.MongoClient("localhost", port=27017)
document = db["quintus"]
document.drop()
