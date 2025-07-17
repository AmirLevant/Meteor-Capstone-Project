from flask import Blueprint, jsonify, request
from urllib import response
import requests
import math
import time
import random
from datetime import datetime
import os
import sys

sys.path.append('..')
import database
import models

route_bp = Blueprint('route', __name__)

API_KEY = os.getenv('API_KEY')

@route_bp.route('/api/routes/create', methods=['POST', 'OPTIONS'])
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
        drivers = data.get('drivers', [])
        
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
        
        # If drivers are provided, divide the area into sectors
        if drivers and len(drivers) > 0:
            sectors = divide_coverage_into_sectors(center, radius, roads, drivers)
            
            # Store each driver's route
            for sector in sectors:
                driver_route = models.Route(
                    driver_id=sector['driver_id'],
                    route_json={
                        'center': center,
                        'radius': radius,
                        'sector': sector['sector_info'],
                        'roads': sector['roads'],
                        'color': sector['color']
                    }
                )
                database.insert_route(driver_route)
            
            return jsonify({
                'success': True,
                'sectors': sectors,
                'message': f'Created {len(sectors)} route sectors for {len(drivers)} drivers'
            })
        else:
            # Original behavior - no drivers specified
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

def get_roads_within_radius(center, radius_km):
    mapbox_token = API_KEY
    
    if not mapbox_token:
        print("Warning: No Mapbox token found, falling back to OpenStreetMap")
        return get_roads_from_overpass(center, radius_km)
    
    print(f"Getting real roads within {radius_km}km of {center['lat']}, {center['lng']}")
    
    try:
        lat_delta = radius_km / 111
        lng_delta = radius_km / (111 * math.cos(math.radians(center['lat'])))
        
        return get_roads_from_overpass(center, radius_km)
        
    except Exception as e:
        print(f"Error getting roads from Mapbox: {e}")
        return get_roads_from_overpass(center, radius_km)

def get_roads_from_overpass(center, radius_km):
    try:
        radius_meters = radius_km * 1000
        
        overpass_url = "http://overpass-api.de/api/interpreter"
        
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
                    coordinates = [[node['lon'], node['lat']] for node in element['geometry']]
                    
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
    R = 6371
    
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
    return f'route_{int(time.time())}_{random.randint(1000, 9999)}'

def divide_coverage_into_sectors(center, radius, roads, drivers):
    sectors = []
    num_drivers = len(drivers)
    angle_per_driver = 360 / num_drivers
    
    # Define colors for sectors
    colors = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
    
    for i, driver in enumerate(drivers):
        start_angle = i * angle_per_driver
        end_angle = (i + 1) * angle_per_driver
        
        # Filter roads for this sector
        sector_roads = []
        for road in roads:
            if road_in_sector(road, center, start_angle, end_angle):
                sector_roads.append(road)
        
        sector = {
            'driver_id': driver.get('id'),
            'driver_name': driver.get('name'),
            'sector_info': {
                'start_angle': start_angle,
                'end_angle': end_angle,
                'index': i
            },
            'roads': sector_roads,
            'color': colors[i % len(colors)]
        }
        sectors.append(sector)
    
    return sectors

def road_in_sector(road, center, start_angle, end_angle):
    # Check if any point of the road is within the sector
    if road.get('geometry') and road['geometry'].get('coordinates'):
        for coord in road['geometry']['coordinates']:
            lng, lat = coord
            angle = calculate_bearing(center['lat'], center['lng'], lat, lng)
            
            # Normalize angle to 0-360
            angle = (angle + 360) % 360
            
            # Check if angle is within sector
            if start_angle <= angle <= end_angle:
                return True
            # Handle wraparound case (e.g., sector from 350 to 10 degrees)
            if start_angle > end_angle and (angle >= start_angle or angle <= end_angle):
                return True
    
    return False

def calculate_bearing(lat1, lng1, lat2, lng2):
    # Calculate bearing from point 1 to point 2
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    lng_diff = math.radians(lng2 - lng1)
    
    x = math.sin(lng_diff) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lng_diff)
    
    bearing = math.atan2(x, y)
    bearing = math.degrees(bearing)
    
    return bearing