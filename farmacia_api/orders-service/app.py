from flask import Flask, request, jsonify
from pymongo import MongoClient
import os
from datetime import datetime

app = Flask(__name__)

# 🔗 Conexión a MongoDB (coincide con docker-compose)
mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/farmacia")
client = MongoClient(mongo_url)
db = client.get_default_database()

@app.route("/", methods=["GET"])
def home():
    return jsonify({"servicio": "Orders Service activo 🧾"})

# 🧾 1️⃣ Crear una orden
@app.route("/orders", methods=["POST"])
def crear_orden():
    data = request.get_json()

    if not data or "sku" not in data or "cantidad" not in data:
        return jsonify({"error": "Debe incluir 'sku' y 'cantidad'"}), 400

    # Buscar el producto en inventario
    lote = db.lote.find_one(
        {"sku": data["sku"]},
        sort=[("fecha_vencimiento", 1)]  # Lote que vence antes (FIFO)
    )

    if not lote:
        return jsonify({"error": "Producto no disponible en inventario"}), 404

    if lote["cantidad"] < data["cantidad"]:
        return jsonify({"error": "Stock insuficiente en el lote actual"}), 400

    # Calcular total desde catálogo
    producto = db.producto.find_one({"sku": data["sku"]})
    if not producto:
        return jsonify({"error": "Producto no encontrado en catálogo"}), 404

    total = data["cantidad"] * producto["precio_unitario"]

    # Actualizar stock del lote
    db.lote.update_one(
        {"_id": lote["_id"]},
        {"$inc": {"cantidad": -data["cantidad"]}}
    )

    # Crear orden
    orden = {
        "sku": data["sku"],
        "nombre_producto": producto["nombre"],
        "lote_vendido": lote["lote"],
        "cantidad": data["cantidad"],
        "precio_unitario": producto["precio_unitario"],
        "total": total,
        "fecha": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    }

    db.orden.insert_one(orden)
    return jsonify({"mensaje": "Orden registrada correctamente", "orden": orden}), 201


# 📋 2️⃣ Listar todas las órdenes
@app.route("/orders", methods=["GET"])
def listar_ordenes():
    ordenes = list(db.orden.find({}, {"_id": 0}))
    if not ordenes:
        return jsonify([{"mensaje": "No hay órdenes"}]), 200
    return jsonify(ordenes), 200


# 🔎 3️⃣ Consultar órdenes por SKU o por fecha
@app.route("/orders/search", methods=["GET"])
def buscar_ordenes():
    sku = request.args.get("sku")
    fecha = request.args.get("fecha")  # formato YYYY-MM-DD
    filtro = {}

    if sku:
        filtro["sku"] = sku
    if fecha:
        filtro["fecha"] = {"$regex": f"^{fecha}"}

    resultados = list(db.orden.find(filtro, {"_id": 0}))
    if not resultados:
        return jsonify([{"mensaje": "No se encontraron órdenes"}]), 200
    return jsonify(resultados), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
