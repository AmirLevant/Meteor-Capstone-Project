from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

# controllers imports
from controllers.manager_controller import plow_bp
from controllers.route_controller import route_bp
from controllers.driver_controller import driver_bp

meteor_app = Flask(__name__)
CORS(meteor_app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Global OPTIONS handler for all routes
@meteor_app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", "http://localhost:5173")
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        return response

meteor_app.register_blueprint(plow_bp)
meteor_app.register_blueprint(route_bp)
meteor_app.register_blueprint(driver_bp)

@meteor_app.route('/')
def home():
    return "Meteor App is running!"

if __name__ == '__main__':
    # Debug: Print all registered routes when server starts
    print("=== Registered Routes ===")
    for rule in meteor_app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule} -> {rule.methods}")
    print("========================")
    
    meteor_app.run(host='localhost', port=5000, debug=True)