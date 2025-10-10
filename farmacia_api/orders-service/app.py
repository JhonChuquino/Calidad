from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from datetime import datetime

app = Flask(__name__)

mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")
client = MongoClient(mongo_url)
db = client["pharma_store_db"]

@app.route("/", methods=["GET"])
def home():
    return jsonify({"service": "Orders Service active 🧾"})

@app.route("/orders", methods=["POST"])
def crear_orden():
    data = request.get_json()
    if not data or "sku" not in data or "quantity" not in data:
        return jsonify({"error": "Fields 'sku' and 'quantity' are required"}), 400

    lote = db.inventory.find_one(
        {"sku": data["sku"]},
        sort=[("expiry_date", 1)]
    )
    if not lote:
        return jsonify({"error": "Product not found in inventory"}), 404
    if lote["quantity"] < data["quantity"]:
        return jsonify({"error": "Not enough stock available"}), 400

    producto = db.product.find_one({"sku": data["sku"]})
    if not producto:
        return jsonify({"error": "Product not found in catalog"}), 404

    unit_price = producto.get("unit_price", 0)
    batch = lote.get("batch", "N/A")
    total = data["quantity"] * unit_price

    db.inventory.update_one(
        {"_id": lote["_id"]},
        {"$inc": {"quantity": -data["quantity"]}}
    )

    orden = {
        "sku": data["sku"],
        "product_name": producto["name"],
        "batch_sold": batch,
        "quantity": data["quantity"],
        "unit_price": unit_price,
        "total": total,
        "date": datetime.utcnow().isoformat()
    }

    db.order.insert_one(orden)
    return jsonify({"message": "Order created successfully", "order": orden}), 201


@app.route("/orders", methods=["GET"])
def listar_ordenes():
    ordenes = list(db.order.find({}, {"_id": 0}))
    if not ordenes:
        return jsonify([{"message": "No orders found"}]), 200
    return jsonify(ordenes), 200


@app.route("/orders/search", methods=["GET"])
def buscar_ordenes():
    sku = request.args.get("sku")
    fecha = request.args.get("fecha")
    filtro = {}
    if sku:
        filtro["sku"] = sku
    if fecha:
        filtro["date"] = {"$regex": f"^{fecha}"}

    resultados = list(db.order.find(filtro, {"_id": 0}))
    if not resultados:
        return jsonify([{"message": "No orders found"}]), 200
    return jsonify(resultados), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
