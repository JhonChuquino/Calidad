from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# 🔗 Conexión a MongoDB
mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/pharma_store_db")
client = MongoClient(mongo_url)
db = client["pharma_store_db"]

@app.route("/", methods=["GET"])
def home():
    return jsonify({"service": "Catalog Service active 🚀"})

# 🧾 Listar catálogo con información del lote más próximo a vencer
@app.route("/catalog", methods=["GET"])
def get_catalog():
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "inventory",         # ✅ antes: lote
                    "localField": "sku",
                    "foreignField": "sku",
                    "as": "inventory_data"
                }
            },
            {
                "$unwind": {
                    "path": "$inventory_data",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$sort": {"inventory_data.expiry_date": 1}
            },
            {
                "$group": {
                    "_id": "$sku",
                    "sku": {"$first": "$sku"},
                    "name": {"$first": "$name"},
                    "category": {"$first": "$category"},
                    "unit_price": {"$first": "$unit_price"},
                    "next_batch": {"$first": "$inventory_data.batch"},
                    "expiry_date": {"$first": "$inventory_data.expiry_date"},
                    "available_quantity": {"$first": "$inventory_data.quantity"}
                }
            }
        ]

        products = list(db.product.aggregate(pipeline))  # ✅ antes: producto

        if not products:
            return jsonify([{"message": "No products found"}]), 200

        return jsonify(products), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

