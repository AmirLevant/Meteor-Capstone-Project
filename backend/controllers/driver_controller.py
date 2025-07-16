from flask import Blueprint, jsonify, request
import sys

# Add parent directory to path for imports
sys.path.append('..')
import database
import models

# Create driver blueprint
driver_bp = Blueprint('driver', __name__)

@driver_bp.route('/api/assign_driver', methods=['POST'])
def assign_driver():
    """Assign a driver to an existing route"""
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

@driver_bp.route('/api/driver', methods=['POST'])
def add_driver():
    """Add a new driver to the database"""
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

@driver_bp.route('/api/driver/location', methods=['PUT'])
def update_driver_position():
    """Update driver's current location"""
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

@driver_bp.route('/api/driver/location', methods=['GET'])
def get_driver_position():
    """Get driver's current location in GeoJSON format"""
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