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

@route_bp.route('/api/routes/create', methods=['POST'])
def create_route():
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
        
        # Generate unique route ID
        route_id = generate_route_id()
        
        # Get roads within the radius using real road data
        roads = get_roads_within_radius(center, radius)
        
        # Create coverage route record
        coverage_route = models.CoverageRoute(
            route_id=route_id,
            center_lat=center['lat'],
            center_lng=center['lng'],
            radius=radius,
            created_at=datetime.now().isoformat(),
            status='active'
        )
        
        # Insert coverage route into database
        print(f"Attempting to save route {route_id} to database...")
        db_route_id = database.insert_coverage_route(coverage_route)
        if not db_route_id:
            print("Failed to save route to database!")
            return jsonify({
                'success': False,
                'error': 'Failed to save route to database'
            }), 500
        
        print(f"Successfully saved route to database with ID: {db_route_id}")
        
        # Create road segment objects
        road_segments = []
        for road in roads:
            segment = models.RoadSegment(
                segment_id=road['id'],
                route_id=route_id,
                name=road['name'],
                road_type=road['type'],
                coordinates=road['geometry']['coordinates'],
                properties=road.get('properties', {})
            )
            road_segments.append(segment)
        
        # Insert road segments into database
        if road_segments:
            print(f"Attempting to save {len(road_segments)} road segments...")
            segment_ids = database.insert_road_segments(road_segments)
            print(f"Successfully inserted {len(segment_ids)} road segments with IDs: {segment_ids[:3]}...")  # Show first 3 IDs
        else:
            print("No road segments to save")
        
        # Prepare lean response for frontend (only display essentials)
        frontend_roads = []
        for road in roads:
            frontend_road = {
                'id': road['id'],
                'name': road['name'],
                'type': road['type'],
                'coordinates': road['geometry']['coordinates']  # Just coordinates, no full geometry wrapper
            }
            frontend_roads.append(frontend_road)
        
        route_response = {
            'id': route_id,
            'center': center,
            'radius': radius,
            'roads': frontend_roads,  # Lean road data
            'road_count': len(frontend_roads),
            'created_at': coverage_route.created_at,
            'status': 'active'
        }
        
        print(f"Route {route_id} created with {len(roads)} roads and saved to database")
        
        return jsonify({
            'success': True,
            'route': route_response,
            'roads': frontend_roads,  # Lean road data
            'message': f'Found {len(roads)} road segments within {radius}km radius'
        })
        
    except Exception as e:
        print(f"Error creating route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to create route',
            'details': str(e)
        }), 500

# NEW: Get all routes
@route_bp.route('/api/routes', methods=['GET'])
def get_routes():
    """Get all active routes from database"""
    try:
        # Get all coverage routes from database
        coverage_routes = database.get_all_coverage_routes()
        
        routes_list = []
        for coverage_route in coverage_routes:
            # Get road segments for this route
            road_segments = database.get_road_segments_by_route_id(coverage_route.route_id)
            
            # Convert road segments to lean format for frontend
            roads = []
            for segment in road_segments:
                road = {
                    'id': segment.segment_id,
                    'name': segment.name,
                    'type': segment.road_type,
                    'coordinates': segment.coordinates  # Direct coordinates array
                }
                roads.append(road)
            
            # Build lean route response
            route_data = {
                'id': coverage_route.route_id,
                'center': {
                    'lat': coverage_route.center_lat,
                    'lng': coverage_route.center_lng
                },
                'radius': coverage_route.radius,
                'roads': roads,
                'road_count': len(roads),
                'created_at': coverage_route.created_at,
                'status': coverage_route.status
            }
            routes_list.append(route_data)
        
        print(f"Returning {len(routes_list)} routes from database")
        return jsonify({
            'success': True,
            'routes': routes_list,
            'count': len(routes_list)
        })
    except Exception as e:
        print(f"Error getting routes from database: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to get routes',
            'details': str(e)
        }), 500

# NEW: Get route by ID
@route_bp.route('/api/routes/<route_id>', methods=['GET'])
def get_route_by_id(route_id):
    """Get a specific route by ID from database"""
    try:
        # Get coverage route from database
        coverage_route = database.get_coverage_route_by_id(route_id)
        if not coverage_route:
            return jsonify({
                'success': False,
                'error': 'Route not found'
            }), 404
        
        # Get road segments for this route
        road_segments = database.get_road_segments_by_route_id(route_id)
        
        # Convert road segments to lean format for frontend
        roads = []
        for segment in road_segments:
            road = {
                'id': segment.segment_id,
                'name': segment.name,
                'type': segment.road_type,
                'coordinates': segment.coordinates  # Direct coordinates array
            }
            roads.append(road)
        
        # Build lean route response
        route_data = {
            'id': coverage_route.route_id,
            'center': {
                'lat': coverage_route.center_lat,
                'lng': coverage_route.center_lng
            },
            'radius': coverage_route.radius,
            'roads': roads,
            'road_count': len(roads),
            'created_at': coverage_route.created_at,
            'status': coverage_route.status
        }
        
        print(f"Returning route {route_id} with {len(roads)} roads from database")
        return jsonify({
            'success': True,
            'route': route_data
        })
    except Exception as e:
        print(f"Error getting route {route_id} from database: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'Failed to get route',
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
    """Get actual roads within radius using OpenStreetMap data"""
    mapbox_token = API_KEY
    
    if not mapbox_token:
        print("Warning: No Mapbox token found, using OpenStreetMap data")
    
    print(f"Getting real roads within {radius_km}km of {center['lat']}, {center['lng']}")
    
    try:
        # Use OpenStreetMap data via Overpass API for real road segments
        return get_roads_from_overpass(center, radius_km)
        
    except Exception as e:
        print(f"Error getting roads: {e}")
        return []

def get_roads_from_overpass(center, radius_km):
    """Get actual roads from OpenStreetMap via Overpass API"""
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