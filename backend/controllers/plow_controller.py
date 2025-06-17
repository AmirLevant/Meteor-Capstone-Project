from flask import Blueprint, jsonify

plow_bp = Blueprint('plows', __name__, url_prefix='/api/plows')

# Route 1: Get all plows
@plow_bp.route('/')
def get_all_plows():
    return jsonify({"plows": [...]})

# Route 2: Get single plow
@plow_bp.route('/<int:plow_id>')
def get_plow_by_id(plow_id):
    return jsonify({"plow_id": plow_id, "name": "Plow Alpha"})

# Route 3: Create new plow
@plow_bp.route('/', methods=['POST'])
def create_plow():
    return jsonify({"message": "Plow created"})

# Route 4: Update plow status
@plow_bp.route('/<int:plow_id>/status', methods=['PATCH'])
def update_status(plow_id):
    return jsonify({"message": f"Plow {plow_id} status updated"})