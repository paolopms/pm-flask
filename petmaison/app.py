from __future__ import annotations

import locale
import os
from datetime import datetime
from decimal import Decimal

from flask import Flask, jsonify, send_from_directory
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user

from .config import get_config
from .extensions import api, csrf, db, login_manager, migrate
from .models import (
    Customer,
    Order,
    Product,
    Purchase,
    PurchaseItem,
    Sale,
    SaleItem,
    StockMovement,
    Supplier,
    User,
)


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(get_config())

    os.makedirs(app.config["MEDIA_ROOT"], exist_ok=True)
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    api.init_app(app)

    # Locale for es-CL formatting
    try:
        locale.setlocale(locale.LC_ALL, "es_CL.utf8")
    except Exception:
        pass

    register_jinja_filters(app)
    register_error_handlers(app)
    register_blueprints(app)
    register_admin(app)

    @app.get("/health")
    def health() -> tuple[dict, int]:
        return {"status": "ok"}, 200

    @app.route('/media/<path:filename>')
    def media(filename: str):
        return send_from_directory(app.config['MEDIA_ROOT'], filename)

    return app


@login_manager.user_loader
def load_user(user_id: str):
    return db.session.get(User, int(user_id))


def register_admin(app: Flask) -> None:
    class SecureModelView(ModelView):
        def is_accessible(self):  # type: ignore[override]
            return current_user.is_authenticated and getattr(current_user, "role", "") == "admin"

    admin = Admin(app, name="PetMaison Admin", template_mode="bootstrap4")
    admin.add_view(SecureModelView(User, db.session))
    admin.add_view(SecureModelView(Product, db.session))
    admin.add_view(SecureModelView(Customer, db.session))
    admin.add_view(SecureModelView(Supplier, db.session))


def register_blueprints(app: Flask) -> None:
    from .blueprints.auth.views import bp as auth_bp
    from .blueprints.dashboard.views import bp as dashboard_bp
    from .blueprints.products.views import bp as products_bp
    from .blueprints.customers.views import bp as customers_bp
    from .blueprints.suppliers.views import bp as suppliers_bp
    from .blueprints.purchases.views import bp as purchases_bp
    from .blueprints.sales.views import bp as sales_bp
    from .blueprints.orders.views import bp as orders_bp
    from .blueprints.inventory.views import bp as inventory_bp
    from .blueprints.reports.views import bp as reports_bp
    from .blueprints.api.views import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(suppliers_bp)
    app.register_blueprint(purchases_bp)
    app.register_blueprint(sales_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(api_bp, url_prefix="/api")


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(403)
    def forbidden(_):
        return (jsonify({"message": "Acceso prohibido"}), 403)

    @app.errorhandler(404)
    def not_found(_):
        return (jsonify({"message": "No encontrado"}), 404)

    @app.errorhandler(500)
    def server_error(_):
        return (jsonify({"message": "Error interno"}), 500)


def register_jinja_filters(app: Flask) -> None:
    def clp(value: Decimal | float | int) -> str:
        try:
            val = Decimal(str(value))
        except Exception:
            return "-"
        # CLP sin decimales
        return f"${int(val):,}".replace(",", ".")

    def es_date(value: datetime) -> str:
        if not value:
            return ""
        return value.strftime("%d-%m-%Y")

    app.jinja_env.filters["clp"] = clp
    app.jinja_env.filters["es_date"] = es_date


app = create_app()
