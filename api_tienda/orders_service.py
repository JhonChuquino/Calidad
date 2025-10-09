# api_tienda/orders_service.py
from flask import Blueprint, jsonify, request
from datetime import datetime
import uuid
from db import inventory_tbl, order_tbl, detail_order_tbl

orders_bp = Blueprint("orders", __name__)

# === Crear orden y descontar stock ===
@orders_bp.route("/", methods=["POST"])
def crear_orden():
    data = request.json or {}
    cliente = data.get("cliente", "Anónimo")
    items = data.get("items", [])
    reservas = []

    if not items:
        return jsonify({"error": "No hay productos en la orden"}), 400

    for item in items:
        product_id = item["product_id"]
        qty = int(item["qty"])

        # Buscar lotes disponibles FEFO (por fecha de caducidad)
        lotes = list(inventory_tbl.find(
            {"product_id": product_id, "cantidad_disponible": {"$gt": 0}}
        ).sort("fecha_caducidad", 1))

        for lote in lotes:
            if qty <= 0:
                break

            disp = int(lote.get("cantidad_disponible", 0))
            if disp <= 0:
                continue

            tomar = min(disp, qty)
            nueva_cant = disp - tomar

            # Descontar en Mongo
            inventory_tbl.update_one(
                {"_id": lote["_id"]},
                {"$set": {"cantidad_disponible": nueva_cant}}
            )

            reservas.append({
                "product_id": product_id,
                "lot": lote["lot"],
                "qty": tomar
            })
            qty -= tomar

        if qty > 0:
            return jsonify({"error": f"Stock insuficiente para {product_id}"}), 409

    # Crear la orden
    order_id = f"O-{uuid.uuid4().hex[:8].upper()}"
    orden_doc = {
        "order_id": order_id,
        "cliente": cliente,
        "fecha": datetime.utcnow().isoformat(),
        "estado": "COMPLETADA"
    }
    order_tbl.insert_one(orden_doc)

    # Crear los detalles
    for i, item in enumerate(items, start=1):
        lotes_usados = [r for r in reservas if r["product_id"] == item["product_id"]]
        detail_order_tbl.insert_one({
            "order_id": order_id,
            "item_n": f"ITEM#{i:03d}",
            "product_id": item["product_id"],
            "qty": int(item["qty"]),
            "lotes_usados": lotes_usados
        })

    return jsonify({
        "msg": "Orden creada exitosamente",
        "order_id": order_id,
        "reservas": reservas
    }), 201
