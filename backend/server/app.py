from flask import Flask, jsonify, request
from flask_cors import CORS
from urllib import response
from dotenv import load_dotenv
import os
import requests
import math
import time
import random
from datetime import datetime

import sys

sys.path.append('..') # Needed for the app.py to index and view the controllers folder
import database
import models

load_dotenv() # Needed for getting the environmental variable API_KEY from the .env file
API_KEY = os.getenv('API_KEY')

# controllers imports
from controllers.plow_controller import plow_bp

meteor_app = Flask(__name__)
CORS(meteor_app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

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

# NEW: Route creation endpoint for coverage area
@meteor_app.route('/api/routes/create', methods=['POST', 'OPTIONS'])
def create_route():
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'OK'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
        
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'center' not in data or 'radius' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: center and radius'
            }), 400
            
        center = data['center']
        radius = data['radius']
        
        if not center.get('lat') or not center.get('lng'):
            return jsonify({
                'success': False,
                'error': 'Center must include lat and lng coordinates'
            }), 400
            
        print(f"Creating route for center: {center['lat']}, {center['lng']} with radius: {radius} km")
        
        # Ensure radius is a number
        try:
            radius = float(radius)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Radius must be a valid number'
            }), 400
        
        # Get roads within the radius using Mapbox API
        roads = get_roads_within_radius(center, radius)
        
        # Create route record
        route = {
            'id': generate_route_id(),
            'center': center,
            'radius': radius,
            'roads': roads,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        return jsonify({
            'success': True,
            'route': route,
            'roads': roads,
            'message': f'Found {len(roads)} road segments within {radius}km radius'
        })
        
    except Exception as e:
        print(f"Error creating route: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create route',
            'details': str(e)
        }), 500

# NEW: Get all routes
@meteor_app.route('/api/routes', methods=['GET'])
def get_routes():
    """Get all active routes"""
    try:
        routes_list = list(active_routes.values())
        print(f"Returning {len(routes_list)} routes")
        return jsonify({
            'success': True,
            'routes': routes_list,
            'count': len(routes_list)
        })
    except Exception as e:
        print(f"Error getting routes: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get routes'
        }), 500

# NEW: Get route by ID
@meteor_app.route('/api/routes/<route_id>', methods=['GET'])
def get_route_by_id(route_id):
    """Get a specific route by ID"""
    try:
        if route_id in active_routes:
            print(f"Returning route {route_id}")
            return jsonify({
                'success': True,
                'route': active_routes[route_id]
            })
        else:
            print(f"Route {route_id} not found. Available routes: {list(active_routes.keys())}")
            return jsonify({
                'success': False,
                'error': 'Route not found'
            }), 404
    except Exception as e:
        print(f"Error getting route {route_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get route'
        }), 500

def get_roads_within_radius(center, radius_km):
    """Get actual roads within radius using Mapbox API"""
    
    # Get Mapbox access token from environment
    mapbox_token = API_KEY
    
    if not mapbox_token:
        print("Warning: No Mapbox token found, falling back to OpenStreetMap")
        return get_roads_from_overpass(center, radius_km)
    
    print(f"Getting real roads within {radius_km}km of {center['lat']}, {center['lng']}")
    
    try:
        # Use Mapbox Directions API to get actual road network
        # Create a bounding box around the center point
        lat_delta = radius_km / 111  # Approximate km per degree of latitude
        lng_delta = radius_km / (111 * math.cos(math.radians(center['lat'])))
        
        # Get roads using Overpass API (OpenStreetMap data) - more reliable for road segments
        return get_roads_from_overpass(center, radius_km)
        
    except Exception as e:
        print(f"Error getting roads from Mapbox: {e}")
        return get_roads_from_overpass(center, radius_km)

def get_roads_from_overpass(center, radius_km):
    """Get actual roads from OpenStreetMap via Overpass API"""
    try:
        # Convert radius to meters
        radius_meters = radius_km * 1000
        
        # Overpass API query for roads within radius
        overpass_url = "http://overpass-api.de/api/interpreter"
        
        # Query for roads (highways) within the radius
        overpass_query = f"""
        [out:json][timeout:25];
        (
          way["highway"~"^(primary|secondary|tertiary|residential|service|unclassified)$"]
          (around:{radius_meters},{center['lat']},{center['lng']});
        );
        out geom;
        """
        
        print(f"Querying Overpass API for roads within {radius_km}km...")
        
        response = requests.post(overpass_url, data=overpass_query, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            roads = []
            
            for element in data.get('elements', []):
                if element.get('type') == 'way' and element.get('geometry'):
                    # Convert OSM way to our road format
                    coordinates = [[node['lon'], node['lat']] for node in element['geometry']]
                    
                    # Only include roads that have multiple points
                    if len(coordinates) >= 2:
                        road = {
                            'id': f"osm_way_{element['id']}",
                            'name': element.get('tags', {}).get('name', f"Road {element['id']}"),
                            'type': element.get('tags', {}).get('highway', 'unclassified'),
                            'geometry': {
                                'type': 'LineString',
                                'coordinates': coordinates
                            },
                            'properties': {
                                'osm_id': element['id'],
                                'highway_type': element.get('tags', {}).get('highway'),
                                'surface': element.get('tags', {}).get('surface', 'unknown')
                            }
                        }
                        roads.append(road)
            
            print(f"Found {len(roads)} actual road segments from OpenStreetMap")
            return roads
            
        else:
            print(f"Overpass API error: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Error getting roads from Overpass API: {e}")
        return []

# Remove the generate_simulated_roads function - we're getting real roads now!

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat/2) * math.sin(delta_lat/2) + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * 
         math.sin(delta_lng/2) * math.sin(delta_lng/2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def generate_route_id():
    """Generate unique route ID"""
    return f'route_{int(time.time())}_{random.randint(1000, 9999)}'

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
    meteor_app.run(host='localhost', port=5000, debug=True)