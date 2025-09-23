import json
import os
import urllib.request

PRODUCTS_URL = os.environ.get("PRODUCTS_API_URL", "")  # URL del microservicio de productos

# Lista temporal en memoria (se reinicia cuando Lambda se recicla)
RESEÑAS = []

def _get_products():
    if not PRODUCTS_URL:
        return []
    try:
        with urllib.request.urlopen(PRODUCTS_URL, timeout=5) as resp:
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except Exception:
        return []

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("rawPath", "/")

    # ---------------- GET /reviews ----------------
    if method == "GET" and path.endswith("/reviews"):
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(RESEÑAS)
        }

    # ---------------- POST /reviews ----------------
    if method == "POST" and path.endswith("/reviews"):
        body_raw = event.get("body") or "{}"
        try:
            body = json.loads(body_raw)
        except:
            body = {}

        product_id = body.get("product_id")
        comentario = body.get("comentario")

        if not product_id or not comentario:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Faltan campos: product_id y comentario"})
            }

        # Validar producto en el otro microservicio
        productos = _get_products()
        existe = any(p.get("id") == product_id for p in productos)

        if not existe:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": f"Producto {product_id} no existe"})
            }

        # Guardar en la lista en memoria
        nueva = {"product_id": product_id, "comentario": comentario}
        RESEÑAS.append(nueva)

        return {
            "statusCode": 201,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Reseña registrada", **nueva})
        }

    # ---------------- Not Found ----------------
    return {"statusCode": 404, "body": "Not Found"}
