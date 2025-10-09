from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")
client = MongoClient(mongo_url)
db = client["pharma_store_db"]

@app.route("/", methods=["GET"])
def home():
    return jsonify({"servicio": "Catalog Service activo 🚀"})

@app.route("/catalog", methods=["GET"])
def get_catalog():
    productos = list(db.producto.find({}, {"_id": 0}))
    if not productos:
        return jsonify([{"mensaje": "Sin productos"}])
    return jsonify(productos)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
