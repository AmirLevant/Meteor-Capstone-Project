from flask import Blueprint, jsonify, request
from urllib import response
import requests
import math
import time
import random
from datetime import datetime
import os
import sys

# Add parent directory to path for imports
sys.path.append('..')
import database
import models

# Create route blueprint
route_bp = Blueprint('route', __name__)

# Get API key from environment
API_KEY = os.getenv('API_KEY')

@route_bp.route('/api/routes/create', methods=['POST', 'OPTIONS'])
def create_route():
    """Create route for coverage area"""
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

@route_bp.route('/api/get_route', methods=['POST'])
def optimized_route():
    """Get optimized route from coordinates"""
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

# Helper functions
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