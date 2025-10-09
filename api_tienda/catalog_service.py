# api_tienda/catalog_service.py
from flask import Blueprint, jsonify, request
from bson import ObjectId
import uuid
from db import product_tbl

catalog_bp = Blueprint("catalog", __name__)

# === Listar productos ===
@catalog_bp.route("/", methods=["GET"])
def listar_productos():
    productos = list(product_tbl.find())
    for p in productos:
        p["_id"] = str(p["_id"])
    return jsonify(productos)

# === Crear producto ===
@catalog_bp.route("/", methods=["POST"])
def crear_producto():
    data = request.json
    pid = data.get("id", f"P-{uuid.uuid4().hex[:8]}")
    item = {
        "id": pid,
        "nombre": data.get("nombre"),
        "descripcion": data.get("descripcion", ""),
        "precio": float(data.get("precio", 0)),
        "categoria": data.get("categoria", ""),
        "estado": "activo"
    }
    result = product_tbl.insert_one(item)
    item["_id"] = str(result.inserted_id)
    return jsonify({"msg": "Producto creado", "producto": item}), 201

# === Obtener producto por ID ===
@catalog_bp.route("/<pid>", methods=["GET"])
def obtener_producto(pid):
    producto = product_tbl.find_one({"id": pid})
    if not producto:
        return jsonify({"error": "No encontrado"}), 404
    producto["_id"] = str(producto["_id"])
    return jsonify(producto)
