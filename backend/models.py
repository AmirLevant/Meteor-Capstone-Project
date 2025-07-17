# Database Model for drivers document
class Driver:
    def __init__(self, name, email, password, position_id):
        self.name = name
        self.email = email
        self.password = password
        self.position_id = position_id  # This is now a reference to positions._id

    def to_dict(self):
        return {
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "position_id": self.position_id
        }

    @staticmethod
    def from_dict(data):
        return Driver(
            name=data["name"],
            email=data["email"],
            password=data["password"],
            position_id=data.get("position_id")
        )


# Database Model for positions document  
class Position:
    def __init__(self, location, last_update):
        self.location = location  # Our driver's GeoJSON file
        self.last_update = last_update

    # Converts the object into a dict for inserting into mongodb
    def to_dict(self):
        return {
            "location": self.location,
            "last_update": self.last_update
        }
    
    # Converts the object from a dict into an object for retrieving from mongodb
    @staticmethod
    def from_dict(data):
        return Position(
            location=data["location"],
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
    def __init__(self, driver_id, route_json):
        self.driver_id = driver_id
        self.route_json = route_json

    def to_dict(self):
        return {
            "driver_id": self.driver_id,
            "route_data": self.route_json  # store full Mapbox response here
        }

    @staticmethod
    def from_dict(data):
        return Route(
            driver_id=data.get("driver_id"),
            route_json=data.get("route_data")
        )

# NEW: Database Model for coverage route document
class CoverageRoute:
    def __init__(self, route_id, center_lat, center_lng, radius, created_at, status="active"):
        self.route_id = route_id
        self.center_lat = center_lat
        self.center_lng = center_lng
        self.radius = radius
        self.created_at = created_at
        self.status = status

    def to_dict(self):
        return {
            "route_id": self.route_id,
            "center_lat": self.center_lat,
            "center_lng": self.center_lng,
            "radius": self.radius,
            "created_at": self.created_at,
            "status": self.status
        }

    @staticmethod
    def from_dict(data):
        return CoverageRoute(
            route_id=data["route_id"],
            center_lat=data["center_lat"],
            center_lng=data["center_lng"],
            radius=data["radius"],
            created_at=data["created_at"],
            status=data.get("status", "active")
        )

# NEW: Database Model for road segment document
class RoadSegment:
    def __init__(self, segment_id, route_id, name, road_type, coordinates, properties=None):
        self.segment_id = segment_id
        self.route_id = route_id
        self.name = name
        self.road_type = road_type
        self.coordinates = coordinates  # List of [longitude, latitude] pairs
        self.properties = properties or {}

    def to_dict(self):
        return {
            "segment_id": self.segment_id,
            "route_id": self.route_id,
            "name": self.name,
            "road_type": self.road_type,
            "coordinates": self.coordinates,
            "properties": self.properties
        }

    @staticmethod
    def from_dict(data):
        return RoadSegment(
            segment_id=data["segment_id"],
            route_id=data["route_id"],
            name=data["name"],
            road_type=data["road_type"],
            coordinates=data["coordinates"],
            properties=data.get("properties", {})
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