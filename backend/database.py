import pymongo

myclient = pymongo.MongoClient("mongodb+srv://admin:manateesareverycool1@cluster0.d2uan.mongodb.net/")
mydb = myclient["database"]

mycol = mydb["company"]
mydict = { "DriverID": "John", "": "Highway 37" }
x = mycol.insert_one(mydict)