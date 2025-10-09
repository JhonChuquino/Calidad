from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")
client = MongoClient(mongo_url)
db = client["pharma_store_db"]

@app.route("/", methods=["GET"])
def home():
    return jsonify({"servicio": "Inventory Service activo 🧾"})

@app.route("/inventory", methods=["GET"])
def listar_inventario():
    inventario = list(db.inventario.find({}, {"_id": 0}))
    if not inventario:
        return jsonify([{"mensaje": "Inventario vacío"}])
    return jsonify(inventario)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
