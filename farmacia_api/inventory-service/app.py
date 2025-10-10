from flask import Flask, jsonify, request
from pymongo import MongoClient
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# 🔗 Conexión a MongoDB
mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")
client = MongoClient(mongo_url)
db = client["pharma_store_db"]

@app.route("/", methods=["GET"])
def home():
    return jsonify({"service": "Inventory Service active 🧾"})

# 🧾 1️⃣ List all inventory
@app.route("/inventory", methods=["GET"])
def list_inventory():
    inventory = list(db.inventory.find({}, {"_id": 0}))
    if not inventory:
        return jsonify([{"message": "Inventory is empty"}]), 200
    return jsonify(inventory), 200

# 🔍 2️⃣ Search product by SKU
@app.route("/inventory/<sku>", methods=["GET"])
def search_by_sku(sku):
    batches = list(db.inventory.find({"sku": sku}, {"_id": 0}).sort("expiry_date", 1))
    if not batches:
        return jsonify({"message": f"No inventory found for SKU {sku}"}), 404
    return jsonify(batches), 200

# ⚠️ 3️⃣ Detect products expiring soon (default: 15 days)
@app.route("/inventory/expiring", methods=["GET"])
def expiring_soon():
    days = int(request.args.get("days", 15))
    limit_date = datetime.utcnow() + timedelta(days=days)

    batches = list(db.inventory.find(
        {"expiry_date": {"$lte": limit_date.strftime("%Y-%m-%d")}},
        {"_id": 0}
    ).sort("expiry_date", 1))

    if not batches:
        return jsonify([{"message": f"No products expiring in the next {days} days"}]), 200
    return jsonify(batches), 200

# 📦 4️⃣ Register new batch in inventory
@app.route("/inventory", methods=["POST"])
def add_batch():
    data = request.get_json()
    if not data or not all(k in data for k in ("sku", "batch", "quantity", "expiry_date")):
        return jsonify({"error": "Missing required fields"}), 400
    
    db.inventory.insert_one({
        "sku": data["sku"],
        "batch": data["batch"],
        "quantity": data["quantity"],
        "entry_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "expiry_date": data["expiry_date"]
    })
    return jsonify({"message": "Batch added successfully"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
