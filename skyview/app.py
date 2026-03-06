from flask import Flask, jsonify, render_template, send_from_directory
import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os

load_dotenv()

MAPPLS_CLIENT_KEY = os.getenv("MAPPLS_CLIENT_KEY")

app = Flask(__name__)

# ---------------- Firebase ----------------

cred = credentials.Certificate("../firebase-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# ---------------- Serve assets ----------------

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('assets', filename)

# ---------------- Home Page ----------------

@app.route("/")
def index():
    return render_template("index.html", mappls_key=MAPPLS_CLIENT_KEY)

# ---------------- Get drones ----------------

@app.route("/drones")
def get_drones():

    drone_docs = db.collection("drones").stream()

    drones = []

    for drone in drone_docs:

        data = drone.to_dict()

        if "geo_location" not in data:
            continue

        loc = data["geo_location"]

        drones.append({
            "id": drone.id,
            "lat": loc.latitude,
            "lng": loc.longitude
        })

    return jsonify(drones)

# ---------------- Run ----------------

if __name__ == "__main__":
    app.run(debug=True)