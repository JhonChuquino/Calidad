from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)
client = MongoClient(os.getenv("MONGO_URL"))
db = client["farmacia"]

@app.route("/inventory", methods=["GET"])
def listar_inventario():
    data = list(db.inventario.find({}, {"_id": 0}))
    return jsonify(data or [{"mensaje": "Inventario vacío"}])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
