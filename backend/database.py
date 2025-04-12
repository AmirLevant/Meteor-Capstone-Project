import pymongo
from backend import models

client = pymongo.MongoClient("mongodb+srv://admin:manateesareverycool1@cluster0.d2uan.mongodb.net/")
db = client["snowplowdb"]

#######################################################################################################

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
    
# Finds and deletes a driver from the database by ID
def delete_driver_by_id(id: str):
    drivers_collection = db["drivers"]

    delete_result = drivers_collection.delete_one({"_id:": id})
    if delete_result:
        return delete_result

#######################################################################################################

# Historical Data Functions:

# Inserts historical_data into the database and returns a string matching the inserted model's id
def insert_historical_data(historical_data: models.HistoricalData):
    collection = db["historical_data"]
    result = collection.insert_one(historical_data.to_dict())
    return str(result.inserted_id)

# Finds and retrieves historical_data from the database by road_id and returns it as a HistoricalData object
def get_historical_data_by_road_id(road_id: str):
    collection = db["historical_data"]
    data = collection.find_one({"historical_information.road_id": road_id})
    if data:
        return models.HistoricalData.from_dict(data)

# Finds and retrieves historical_data from the database by id and returns it as a HistoricalData object
def get_historical_data_by_id(id: str):
    collection = db["historical_data"]
    data = collection.find_one({"_id": ObjectId(id)})
    if data:
        return models.HistoricalData.from_dict(data)

# Finds and deletes a driver from the database by ID
def delete_historical_data_by_id(id: str):
    collection = db["historical_data"]
    result = collection.delete_one({"_id": ObjectId(id)})
    return result

#######################################################################################################

# Road Functions:

# Inserts a road into the database and returns a string matching the inserted model's id
def insert_road(road: models.Road):
    collection = db["roads"]
    result = collection.insert_one(road.to_dict())
    return str(result.inserted_id)

# Finds and retrieves a road from the database by name and returns it as a Road object
def get_road_by_name(name: str):
    collection = db["roads"]
    data = collection.find_one({"route_information.road_name": name})
    if data:
        return models.Road.from_dict(data)

# Finds and retrieves a road from the database by id and returns it as a Road object
def get_road_by_id(id: str):
    collection = db["roads"]
    data = collection.find_one({"_id": ObjectId(id)})
    if data:
        return models.Road.from_dict(data)

# Finds and deletes a road from the database by ID
def delete_road_by_id(id: str):
    collection = db["roads"]
    result = collection.delete_one({"_id": ObjectId(id)})
    return result

#######################################################################################################

# Route Functions:

# Inserts a route into the database and returns a string matching the inserted model's id
def insert_route(route: models.Route):
    collection = db["routes"]
    result = collection.insert_one(route.to_dict())
    return str(result.inserted_id)

# Inserts a route into the database and returns a string matching the inserted model's id
def get_route_by_driver_id(driver_id: str):
    collection = db["routes"]
    data = collection.find_one({"route_information.driver_id": driver_id})
    if data:
        return models.Route.from_dict(data)

# Finds and retrieves a route from the database by id and returns it as a Route object
def get_route_by_id(id: str):
    collection = db["routes"]
    data = collection.find_one({"_id": ObjectId(id)})
    if data:
        return models.Route.from_dict(data)

# Finds and deletes a route from the database by ID
def delete_route_by_id(id: str):
    collection = db["routes"]
    result = collection.delete_one({"_id": ObjectId(id)})
    return result

#######################################################################################################

# SnowCondition Functions:

# Inserts a snow_conditions into the database and returns a string matching the inserted model's id
def insert_snow_condition(condition: models.SnowCondition):
    collection = db["snow_conditions"]
    result = collection.insert_one(condition.to_dict())
    return str(result.inserted_id)

# Finds and retrieves snow_conditions from the database by road_id and returns it as a SnowCondition object
def get_snow_condition_by_road_id(road_id: str):
    collection = db["snow_conditions"]
    data = collection.find_one({"SnowCondition_information.road_id": road_id})
    if data:
        return models.SnowCondition.from_dict(data)

# Finds and retrieves snow_conditions from the database by id and returns it as a SnowCondition object
def get_snow_condition_by_id(id: str):
    collection = db["snow_conditions"]
    data = collection.find_one({"_id": ObjectId(id)})
    if data:
        return models.SnowCondition.from_dict(data)

# Finds and deletes a route from the database by ID
def delete_snow_condition_by_id(id: str):
    collection = db["snow_conditions"]
    result = collection.delete_one({"_id": ObjectId(id)})
    return result
