# api_tienda/inventory_service.py
from flask import Blueprint, jsonify, request
from datetime import datetime
import uuid
from db import inventory_tbl

inventory_bp = Blueprint("inventory", __name__)

# === Crear lote ===
@inventory_bp.route("/lots", methods=["POST"])
def crear_lote():
    data = request.json or {}
    required = ["product_id", "fecha_caducidad", "cantidad_total"]
    for campo in required:
        if campo not in data:
            return jsonify({"error": f"Falta el campo '{campo}'"}), 400

    lote_id = f"L{uuid.uuid4().hex[:6].upper()}"
    sk = f"LOT#{data['fecha_caducidad'].replace('-', '')}#{lote_id}"

    item = {
        "product_id": data["product_id"],
        "lot": sk,
        "lote_id": lote_id,
        "fecha_caducidad": data["fecha_caducidad"],
        "cantidad_total": int(data["cantidad_total"]),
        "cantidad_disponible": int(data.get("cantidad_disponible", data["cantidad_total"])),
        "estado": "activo",
        "fecha_ingreso": datetime.utcnow().isoformat()
    }

    inventory_tbl.insert_one(item)
    item["_id"] = str(item.get("_id", ""))
    return jsonify({"msg": "Lote creado", "lote": item}), 201

# === Listar lotes por producto ===
@inventory_bp.route("/lots/<product_id>", methods=["GET"])
def listar_lotes(product_id):
    lotes = list(inventory_tbl.find(
        {"product_id": product_id, "cantidad_disponible": {"$gt": 0}}
    ).sort("fecha_caducidad", 1))
    for l in lotes:
        l["_id"] = str(l["_id"])
    return jsonify(lotes)
