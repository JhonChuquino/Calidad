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
    return jsonify({"servicio": "Inventory Service activo 🧾"})

# 🧾 1️⃣ Listar todo el inventario
@app.route("/inventory", methods=["GET"])
def listar_inventario():
    inventario = list(db.lote.find({}, {"_id": 0}))
    if not inventario:
        return jsonify([{"mensaje": "Inventario vacío"}]), 200
    return jsonify(inventario), 200

# 🔍 2️⃣ Buscar un producto específico por SKU
@app.route("/inventory/<sku>", methods=["GET"])
def buscar_por_sku(sku):
    lotes = list(db.lote.find({"sku": sku}, {"_id": 0}).sort("fecha_vencimiento", 1))
    if not lotes:
        return jsonify({"mensaje": f"No se encontró inventario para el producto {sku}"}), 404
    return jsonify(lotes), 200

# ⚠️ 3️⃣ Detectar productos próximos a vencer (por ejemplo, en los próximos N días)
@app.route("/inventory/expiring", methods=["GET"])
def proximos_a_vencer():
    dias = int(request.args.get("days", 15))  # por defecto 15 días
    fecha_limite = datetime.utcnow() + timedelta(days=dias)

    lotes = list(db.lote.find(
        {"fecha_vencimiento": {"$lte": fecha_limite.strftime("%Y-%m-%d")}},
        {"_id": 0}
    ).sort("fecha_vencimiento", 1))

    if not lotes:
        return jsonify([{"mensaje": f"No hay productos que venzan en {dias} días"}]), 200
    return jsonify(lotes), 200

# 📦 4️⃣ Registrar nueva entrada de inventario (opcional)
@app.route("/inventory", methods=["POST"])
def agregar_lote():
    data = request.get_json()
    if not data or not all(k in data for k in ("sku", "lote", "cantidad", "fecha_vencimiento")):
        return jsonify({"error": "Faltan campos requeridos"}), 400
    
    db.lote.insert_one({
        "sku": data["sku"],
        "lote": data["lote"],
        "cantidad": data["cantidad"],
        "fecha_ingreso": datetime.utcnow().strftime("%Y-%m-%d"),
        "fecha_vencimiento": data["fecha_vencimiento"]
    })
    return jsonify({"mensaje": "Lote agregado correctamente"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

