from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)
client = MongoClient(os.getenv("MONGO_URL"))
db = client["farmacia"]

@app.route("/orders", methods=["POST"])
def crear_orden():
    data = request.get_json()
    db.orden.insert_one(data)
    return jsonify({"mensaje": "Orden registrada correctamente"}), 201

@app.route("/orders", methods=["GET"])
def listar_ordenes():
    data = list(db.orden.find({}, {"_id": 0}))
    return jsonify(data or [{"mensaje": "No hay órdenes"}])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
