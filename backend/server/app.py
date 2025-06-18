# required imports
from flask import Flask, jsonify, request
from flask_cors import CORS
from urllib import response
import database
import models
from dotenv import load_dotenv
import os

import sys
sys.path.append('..') # Needed for the app.py to index and view the controllers folder

load_dotenv() # Needed for getting the environmental variable API_KEY from the .env file
API_KEY = os.getenv('API_KEY')

# controllers imports
from controllers.plow_controller import plow_bp

meteor_app = Flask(__name__)
CORS(meteor_app)

meteor_app.register_blueprint(plow_bp)


@meteor_app.route('/') # when someone visits the root URL, we run the function home
def home():
    return "Meteor App is running!"

@meteor_app.route('/api/plows')
def get_plows():
    return {
        "plows": [
            {"id": 1, "name": "Plow Alpha", "lat": 45.5017, "lng": -73.5673},
            {"id": 2, "name": "Plow Beta", "lat": 45.5088, "lng": -73.5878}
        ]
    }

# Currently takes and returns a json for the coordinates and route as a POST to get the information for the api call. with this format
#{
# "coordinates": [
#    {"lat": 45.5017, "lng": -73.5673},
#    {"lat": 45.5088, "lng": -73.5878},
#    {"lat": 45.5123, "lng": -73.5699}
# ]
#}
@meteor_app.route('/api/get_route', methods=['POST'])
def optimized_route():
    
    data = request.json
    coordinates = data.get('coordinates')

    if not coordinates or len(coordinates) < 2:
        return jsonify({'error': 'Requires two roads to make a route.'}), 400

    coordinates = ';'.join([f"{pt['lng']},{pt['lat']}" for pt in coordinates])
    
    url = f"https://api.mapbox.com/optimized-trips/v1/mapbox/driving/{coordinates}"
    params = {
        'access_token': API_KEY,
        'geometries': 'geojson',
        'overview': 'full',
        'source': 'first',
        'destination': 'last'
    }

    #Inserts route into database
    route_data = response.json()
    route = models.Route(driver_id=None, route_json=route_data)
    inserted_id = database.insert_route(route)

    route = request.get(url, params=params)
    return jsonify(response.json())

# Allows for the adding of a driver to an existing route in the database
@meteor_app.route('/api/assign_driver', methods=['POST'])
def assign_driver():
    data = request.json
    driver_name = data.get("driver_name")
    route_id = data.get("route_id")

    if not driver_name or not route_id:
        return jsonify({"error": "Missing driver_name or route_id"}), 400

    driver_data = database.get_driver_by_name(driver_name)
    if not driver_data:
        return jsonify({"error": "Driver not found"}), 404

    driver_id = str(driver_data["_id"])
    success = database.assign_driver_to_route(route_id, driver_id)

# Allows for the front-end to add a driver to the database.
@meteor_app.route('/api/driver', methods=['POST'])
def add_driver():
    data = request.json
    required = ["name", "email", "password", "latitude", "longitude", "last_update"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required driver fields"}), 400

    driver = models.Driver(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        last_update=data["last_update"]
    )

# Allow for updating an existing driver's location by giving a geoJSON
@meteor_app.route('/api/driver/location', methods=['PUT'])
def update_driver_pos():
    data = request.json
    required = ["email", "location", "last_update"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required fields"}), 400

    location = data["location"]
    longitude, latitude = location["coordinates"]

    updated = database.update_driver_location(
        email=data["email"],
        longitude=longitude,
        latitude=latitude,
        timestamp=data["last_update"]
    )

    if not updated:
        return jsonify({"error": "Driver not found or update failed"}), 404

    return jsonify({"message": "Location updated successfully"})


# Allows for getting an existing driver's location in GeoJSON format
@meteor_app.route('/api/driver/location', methods=['GET'])
def get_driver_location():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email query parameter is required"}), 400

    driver = database.get_driver_by_email(email)
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    geojson_feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": driver.location["coordinates"]
        },
        "properties": {
            "name": driver.name,
            "email": driver.email,
            "last_update": driver.last_update
        }
    }

    return jsonify(geojson_feature)

if __name__ == '__main__':
    meteor_app.run()