from flask import Flask
from flask_cors import CORS

meteor_app = Flask(__name__)
CORS(meteor_app)

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

if __name__ == '__main__':
    meteor_app.run()