from flask import Flask, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# ✅ Conexión a MongoDB (usa variable de entorno si existe)
mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/farmacia")
client = MongoClient(mongo_url)
db = client.get_default_database()  # Usa directamente la DB definida en la URL

@app.route("/", methods=["GET"])
def home():
    return jsonify({"servicio": "Catalog Service activo 🚀"})

@app.route("/catalog", methods=["GET"])
def get_catalog():
    try:
        pipeline = [
            {
                "$lookup": {
                    "from": "lote",
                    "localField": "sku",
                    "foreignField": "sku",
                    "as": "lotes"
                }
            },
            {
                "$unwind": {
                    "path": "$lotes",
                    "preserveNullAndEmptyArrays": True
                }
            },
            {
                "$sort": {"lotes.fecha_vencimiento": 1}
            },
            {
                "$group": {
                    "_id": "$sku",
                    "nombre": {"$first": "$nombre"},
                    "categoria": {"$first": "$categoria"},
                    "precio_unitario": {"$first": "$precio_unitario"},
                    "lote_proximo": {"$first": "$lotes.lote"},
                    "fecha_vencimiento": {"$first": "$lotes.fecha_vencimiento"},
                    "cantidad_disponible": {"$first": "$lotes.cantidad"}
                }
            }
        ]

        productos = list(db.producto.aggregate(pipeline))

        if not productos:
            return jsonify([{"mensaje": "Sin productos"}]), 200

        return jsonify(productos), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Escucha en todas las interfaces, ideal para Docker
    app.run(host="0.0.0.0", port=5000)
