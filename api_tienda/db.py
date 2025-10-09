# api_tienda/db.py
from pymongo import MongoClient

# 🔹 Conexión local (más adelante cambiarás por IP privada de Mongo en EC2)
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "pharma_store_db"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

product_tbl = db["product"]
inventory_tbl = db["inventory"]
order_tbl = db["order"]
detail_order_tbl = db["detail_order"]


print("✅ Conectado a MongoDB:", MONGO_URI)
