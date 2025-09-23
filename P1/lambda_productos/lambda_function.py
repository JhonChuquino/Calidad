import json

PRODUCTOS = [
    {"id": 1, "nombre": "Laptop"},
    {"id": 2, "nombre": "Celular"},
    {"id": 3, "nombre": "Audífonos"}
]

def lambda_handler(event, context):
    # HTTP API (proxy): event trae routeKey, rawPath, etc.
    # Solo exponemos GET /products
    path = event.get("rawPath", "/")
    method = event.get("requestContext", {}).get("http", {}).get("method", "GET")

    if method == "GET" and path.endswith("/products"):
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(PRODUCTOS)
        }

    return {"statusCode": 404, "body": "Not Found"}
