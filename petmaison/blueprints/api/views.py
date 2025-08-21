from __future__ import annotations

from datetime import datetime

from flask import Blueprint
from flask_smorest import Blueprint as SmorestBlueprint
from marshmallow import Schema, fields

from ...extensions import api, db
from ...models import Product, Sale

api_bp = Blueprint("api_bp", __name__)


class ProductQuerySchema(Schema):
    search = fields.String(load_default=None)
    category = fields.String(load_default=None)
    brand = fields.String(load_default=None)
    active = fields.Boolean(load_default=None)


class ProductSchema(Schema):
    id = fields.Integer()
    sku = fields.String()
    name = fields.String()
    brand = fields.String(allow_none=True)
    category = fields.String(allow_none=True)
    price_gross = fields.Decimal(as_string=True)


sm_products = SmorestBlueprint("api_products", __name__, url_prefix="/products", description="Productos")


@sm_products.route("")
@sm_products.arguments(ProductQuerySchema, location="query")
@sm_products.response(200, ProductSchema(many=True))
def list_products(args):
    q = db.select(Product)
    if args.get("search"):
        like = f"%{args['search']}%"
        q = q.filter(db.or_(Product.name.ilike(like), Product.sku.ilike(like)))
    if args.get("category"):
        q = q.filter(Product.category == args["category"])
    if args.get("brand"):
        q = q.filter(Product.brand == args["brand"])
    if args.get("active") is not None:
        q = q.filter(Product.active == args["active"])
    return db.session.execute(q.limit(200)).scalars().all()


sm_reports = SmorestBlueprint("api_reports", __name__, url_prefix="/reports", description="Reportes")


class SalesQuerySchema(Schema):
    fro = fields.Date(required=True, data_key="from")
    to = fields.Date(required=True)
    groupBy = fields.String(load_default="month")


class SalesReportItem(Schema):
    period = fields.String()
    total = fields.Decimal(as_string=True)


@sm_reports.route("/sales")
@sm_reports.arguments(SalesQuerySchema, location="query")
@sm_reports.response(200, SalesReportItem(many=True))
def report_sales(args):
    fro = args["fro"]
    to = args["to"]
    rows = db.session.execute(
        db.select(db.func.to_char(Sale.date, "YYYY-MM").label("period"), db.func.sum(Sale.total))
        .filter(Sale.date >= fro, Sale.date <= to, Sale.status == "CONFIRMED")
        .group_by(db.text("period"))
        .order_by(db.text("period"))
    ).all()
    return [{"period": p, "total": t or 0} for p, t in rows]


# Register smorest blueprints with the Api
api.register_blueprint(sm_products)
api.register_blueprint(sm_reports)
