import os
#from .. import database
from flask import Flask, jsonify, request
from dotenv import load_dotenv
import httpx
import asyncio

load_dotenv()  # Loads variables from the .env file into the applicaiton  (ex. os.getenv("API_KEY"))

app = Flask(__name__)

# ROUTES

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# Just testing the API and routing commands here, not necessarily for actual implementation - But will keep as is a good example of how to use the API
@app.route("/api/search/<query>")
async def api_search(query):

    try:
        params = request.args.to_dict()
        token = os.getenv("API_KEY")
        
        base_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{query}.json?access_token={token}"

        if params:
            url = base_url + "&" + "&".join(f"{key}={value}" for key, value in params.items())
        else:
            url = base_url

        async with httpx.AsyncClient() as client:
            response = await client.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            return {"error": "Request failed", "status_code": response.status_code}
    
    except Exception as e:
        return jsonify({"error: ": str(e)}), 500     # Something went wrong

if __name__ == "__main__":
    host = os.getenv("FLASK_IP", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 25601))

    app.run(host=host, port=port)