import pymongo
import socket
if socket.gethostname() == "ISZ4DI1Z6MV6Z6K":
    import config
else:
    import product_config as config

def get_mongo(collection_name):
    client = pymongo.MongoClient(config.MONGO_URL)
    mongodb = client['weibo']
    collection = mongodb[collection_name]
    return collection

user_mongo = get_mongo("users_id")
users = user_mongo.find()
with open("users.txt","a") as file:
    num = 0
    for user in users:
        print(num)
        num+=1
        file.write(user["id"])
        file.write("\n")