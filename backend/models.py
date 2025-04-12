# Database Model for drivers document
class Driver:
    def __init__(self, name, email, password, latitude, longitude, last_update):
        self.name = name
        self.email = email
        self.password = password
        self.location = {"latitude": latitude, "longitude": longitude}
        self.last_update = last_update

    # Converts the object into a dict for inserting into mongodb
    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "last_update": self.last_update,
            "location": self.location
        }

    # Converts the object from a dict into an object for retrieving from mongodb
    def from_dict(data):
        return Driver(
            name=data["name"],
            email=data["email"],
            password=data["password"],
            latitude=data["location"]["latitude"],
            longitude=data["location"]["longitude"],
            last_update=data["last_update"]
        )

# Database Model for historial_data document
class HistoricalData:
    def __init__(self, road_id, activity_type, timestamp):
        self.road_id = road_id
        self.activity_type = activity_type
        self.timestamp = timestamp

    def to_dict(self):
        return {
            "historical_information": {
                "road_id": self.road_id,
                "activity_type": self.activity_type,
                "timestamp": self.timestamp
            }
        }

    @staticmethod
    def from_dict(data):
        info = data["historical_information"]
        return HistoricalData(
            road_id=info["road_id"],
            activity_type=info["activity_type"],
            timestamp=info["timestamp"]
        )

# Database Model for road document
class Road:
    def __init__(self, road_name, priority_level, coordinates):
        self.road_name = road_name
        self.priority_level = priority_level
        self.coordinates = coordinates  # List of [longitude, latitude] pairs

    def to_dict(self):
        return {
            "route_information": {
                "road_name": self.road_name,
                "priority_level": self.priority_level,
                "geospatial_data": {
                    "type": "LineString",
                    "coordinates": self.coordinates
                }
            }
        }

    @staticmethod
    def from_dict(data):
        info = data["route_information"]
        return Road(
            road_name=info["road_name"],
            priority_level=info["priority_level"],
            coordinates=info["geospatial_data"]["coordinates"]
        )

# Database Model for route document
class Route:
    def __init__(self, driver_id, route_id, start_latitude, start_longitude, end_latitude, end_longitude):
        self.driver_id = driver_id
        self.route_id = route_id
        self.start_point = {"latitude": start_latitude, "longitude": start_longitude}
        self.end_point = {"latitude": end_latitude, "longitude": end_longitude}

    def to_dict(self):
        return {
            "route_information": {
                "driver_id": self.driver_id,
                "route_id": self.route_id,
                "start_point": self.start_point,
                "end_point": self.end_point
            }
        }

    @staticmethod
    def from_dict(data):
        info = data["route_information"]
        return Route(
            driver_id=info["driver_id"],
            route_id=info["route_id"],
            start_latitude=info["start_point"]["latitude"],
            start_longitude=info["start_point"]["longitude"],
            end_latitude=info["end_point"]["latitude"],
            end_longitude=info["end_point"]["longitude"]
        )

# Database Model for snow_condition document
class SnowCondition:
    def __init__(self, road_id, timestamp, snow_depth, ice_percentage, condition_status):
        self.road_id = road_id
        self.timestamp = timestamp
        self.snow_depth = snow_depth
        self.ice_percentage = ice_percentage
        self.condition_status = condition_status

    def to_dict(self):
        return {
            "SnowCondition_information": {
                "road_id": self.road_id,
                "timestamp": self.timestamp,
                "snow_depth": self.snow_depth,
                "ice_percentage": self.ice_percentage,
                "condition_status": self.condition_status
            }
        }

    @staticmethod
    def from_dict(data):
        info = data["SnowCondition_information"]
        return SnowCondition(
            road_id=info["road_id"],
            timestamp=info["timestamp"],
            snow_depth=info["snow_depth"],
            ice_percentage=info["ice_percentage"],
            condition_status=info["condition_status"]
        )