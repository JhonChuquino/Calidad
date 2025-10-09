from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# ✅ Conexión a MongoDB (coincide con docker-compose)
mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")
client = MongoClient(mongo_url)
db = client["pharma_store_db"]

@app.route("/", methods=["GET"])
def home():
    return jsonify({"servicio": "Orders Service activo 🧾"})

@app.route("/orders", methods=["POST"])
def crear_orden():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Datos no proporcionados"}), 400
    
    db.orden.insert_one(data)
    return jsonify({"mensaje": "Orden registrada correctamente"}), 201

@app.route("/orders", methods=["GET"])
def listar_ordenes():
    ordenes = list(db.orden.find({}, {"_id": 0}))
    if not ordenes:
        return jsonify([{"mensaje": "No hay órdenes"}])
    return jsonify(ordenes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
