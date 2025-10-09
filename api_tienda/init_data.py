# api_tienda/init_data.py
from db import product_tbl, inventory_tbl

def init_all():
    # Insertar producto base si la colección está vacía
    if product_tbl.count_documents({}) == 0:
        sample = {
            "id": "P-001",
            "nombre": "Ibuprofeno 400mg",
            "descripcion": "Analgésico y antiinflamatorio",
            "precio": 3.5,
            "categoria": "Medicamentos"
        }
        product_tbl.insert_one(sample)
        print("🧩 Producto inicial creado.")

    if inventory_tbl.count_documents({}) == 0:
        stock = {
            "product_id": "P-001",
            "lote": "LOT#20251009#001",
            "cantidad_total": 50,
            "cantidad_disponible": 50,
            "fecha_caducidad": "2026-10-09"
        }
        inventory_tbl.insert_one(stock)
        print("📦 Inventario inicial creado.")

    print("✅ Datos iniciales cargados.")
