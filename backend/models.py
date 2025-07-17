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