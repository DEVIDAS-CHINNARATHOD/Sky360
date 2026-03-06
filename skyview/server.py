from flask import Flask, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, firestore
from geopy.distance import geodesic

app = Flask(__name__)

# Firebase setup
cred = credentials.Certificate("../firebase-key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# simulated drones
drones = {
    "A": (13.114, 77.635),
    "B": (13.110, 77.630),
    "C": (13.120, 77.640)
}

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/mission")
def mission():

    docs = db.collection("incidents").limit(1).stream()

    incident = None

    for doc in docs:
        incident = doc.to_dict()

    if incident is None:
        return jsonify({
            "status": "no incident",
            "drones": drones
        })

    loc = incident["location"]
    incident_point = (loc.latitude, loc.longitude)

    nearest = None
    min_dist = 999999

    for d, coord in drones.items():

        dist = geodesic(coord, incident_point).meters

        if dist < min_dist:
            min_dist = dist
            nearest = d

    return jsonify({
        "incident": incident_point,
        "drones": drones,
        "selected_drone": nearest
    })


if __name__ == "__main__":
    app.run(debug=True)