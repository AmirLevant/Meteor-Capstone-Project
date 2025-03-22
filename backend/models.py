import pymongo

# Database Model for drivers
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