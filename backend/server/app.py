import os
#from .. import database
from flask import Flask, jsonify
from dotenv import load_dotenv

load_dotenv()  # Loads variables from the .env file into the applicaiton  (ex. os.getenv("API_KEY"))

app = Flask(__name__)

# ROUTES

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/api/search/")
def api_search():
    return jsonify({'success': True})

if __name__ == "__main__":
    host = os.getenv("FLASK_IP", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 25601))

    app.run(host=host, port=port)