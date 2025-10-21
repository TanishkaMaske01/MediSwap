# File: app.py
# Description: Flask API backend for handling MediSwap pickup requests.
# It receives JSON data, saves it to a local JSON file, and assigns a unique ID.

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import random
import time

app = Flask(__name__)
# Enable CORS for all routes, allowing the frontend HTML file (running locally)
# to communicate with this Flask server.
CORS(app)

DATA_FILE = 'pickup_requests.json'

def load_data():
    """Loads existing pickup request data from the JSON file."""
    if not os.path.exists(DATA_FILE) or os.stat(DATA_FILE).st_size == 0:
        return []
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Warning: {DATA_FILE} is corrupted or empty. Starting with an empty list.")
        return []

def save_data(data):
    """Saves the current list of pickup requests to the JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def index():
    """Basic index route for testing the API server status."""
    return "MediSwap Pickup API is running!", 200

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint for the frontend to check if the server is up."""
    return jsonify({"status": "up", "service": "MediSwap API"}), 200

@app.route('/submit-pickup', methods=['POST'])
def submit_pickup():
    """Endpoint to receive and process new pickup requests."""
    
    # 1. Input Validation
    if not request.json:
        return jsonify({"error": "Missing JSON data in request"}), 400

    required_fields = ['name', 'contact', 'address', 'medicineType']
    for field in required_fields:
        if field not in request.json or not request.json[field]:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    try:
        new_request = request.json
        requests = load_data()

        # 2. Generate Unique ID (Simulation)
        # Using timestamp and a random number for a unique-ish ID
        # In a real database, this would be an auto-incrementing ID.
        request_id = int(time.time() * 1000) % 10000 + random.randint(1000, 9999)
        new_request['request_id'] = request_id
        new_request['status'] = 'Pending'
        
        # 3. Add to Data and Save
        requests.append(new_request)
        save_data(requests)

        print(f"\n--- NEW PICKUP REQUEST RECEIVED ---")
        print(f"ID: {request_id}")
        print(f"Name: {new_request['name']}")
        print(f"Address: {new_request['address']}")
        print("-----------------------------------")

        # 4. Respond to Client
        return jsonify({
            "message": "Pickup request successfully submitted.",
            "request_id": request_id,
            "status": new_request['status']
        }), 200

    except Exception as e:
        print(f"Server Error: {e}")
        return jsonify({"error": "An internal server error occurred during processing."}), 500

if __name__ == '__main__':
    # Running on localhost port 5000, which is referenced in the frontend
    app.run(debug=True)
