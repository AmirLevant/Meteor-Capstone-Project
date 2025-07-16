from flask import Blueprint

plow_bp = Blueprint('plow', __name__)

@plow_bp.route('/api/plows')
def get_plows():
    return {
        "plows": [
            {"id": 1, "name": "Plow Alpha", "lat": 45.5017, "lng": -73.5673},
            {"id": 2, "name": "Plow Beta", "lat": 45.5088, "lng": -73.5878}
        ]
    }