import pymongo
from backend import models

client = pymongo.MongoClient("mongodb+srv://admin:manateesareverycool1@cluster0.d2uan.mongodb.net/")
db = client["snowplowdb"]


# Driver Functions:

# Inserts a driver into the database and returns a string matching the inserted model's id
def insert_driver(driver: models.Driver):
    drivers_collection = db["drivers"]

    result = drivers_collection.insert_one(driver.to_dict())

    return str(result.inserted_id)

# Finds and retrieves a driver from the database by email and returns it as a Driver object
def get_driver_by_email(email: str):
    drivers_collection = db["drivers"]

    driver_data = drivers_collection.find_one({"email": email})
    if driver_data:
        return models.Driver.from_dict(driver_data)

# Finds and retrieves a driver from the database by id and returns it as a Driver object
def get_driver_by_id(id: str):
    drivers_collection = db["drivers"]

    driver_data = drivers_collection.find_one({"_id": id})
    if driver_data:
        return models.Driver.from_dict(driver_data)