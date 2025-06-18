# required imports
from flask import Flask, jsonify, request
from flask_cors import CORS

from urllib import response

from dotenv import load_dotenv
import os

import sys

sys.path.append('..') # Needed for the app.py to index and view the controllers folder
import requests
import database
import models

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

    response = requests.get(url, params=params)

    route_data = response.json()
    route = models.Route(driver_id=None, route_json=route_data)
    database.insert_route(route)

    return jsonify(route_data)


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

    if not success:
        return jsonify({"error": "Failed to assign driver to route"}), 500
    return jsonify({"message": "Driver assigned successfully"})


# Allows for the front-end to add a driver to the database without adding a location.
@meteor_app.route('/api/driver', methods=['POST'])
def add_driver():
    data = request.json
    required = ["name", "email", "password"]
    if not all(field in data for field in required):
        return jsonify({"error": "Missing required driver fields"}), 400

    driver = models.Driver(
        name=data["name"],
        email=data["email"],
        password=data["password"],
        position_id=None
    )
    driver_id = database.insert_driver(driver)

    return jsonify({"message": "Driver added successfully", "driver_id": driver_id}), 201

# Allow for updating an existing driver's location by giving a geoJSON
@meteor_app.route('/api/driver/location', methods=['PUT'])
def update_driver_position():
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
def get_driver_position():
    email = request.args.get("email")
    if not email:
        return jsonify({"error": "Email query parameter is required"}), 400

    driver = database.get_driver_by_email(email)
    if not driver:
        return jsonify({"error": "Driver not found"}), 404

    position = database.get_position_by_id(driver.position_id)
    if not position:
        return jsonify({"error": "Position not found"}), 404

    geojson = {
        "type": "Feature",
        "geometry": position.location,
        "properties": {
            "last_update": position.last_update
        }
    }

    return jsonify(geojson)

if __name__ == '__main__':
    meteor_app.run()