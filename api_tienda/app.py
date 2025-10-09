from flask import Flask, jsonify
from catalog_service import catalog_bp
from inventory_service import inventory_bp
from orders_service import orders_bp
from init_data import init_all

app = Flask(__name__)

# Cargar datos iniciales si no existen
init_all()

# Registrar microservicios
app.register_blueprint(catalog_bp, url_prefix="/catalog")
app.register_blueprint(inventory_bp, url_prefix="/inventory")
app.register_blueprint(orders_bp, url_prefix="/orders")

@app.route("/")
def home():
    return jsonify({"msg": "API Tienda funcionando correctamente"})

# 👇 Asegúrate de tener este bloque
if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)


