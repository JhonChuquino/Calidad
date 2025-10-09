from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)
client = MongoClient(os.getenv("MONGO_URL"))
db = client["farmacia"]

@app.route("/catalog", methods=["GET"])
def get_catalog():
    productos = list(db.producto.find({}, {"_id": 0}))
    if not productos:
        return jsonify([{"mensaje": "Sin productos"}])
    return jsonify(productos)
@app.route("/")
def home():
    return "✅ Catalog Service running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

