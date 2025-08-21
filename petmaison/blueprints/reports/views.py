from __future__ import annotations

import csv
from datetime import datetime
from io import StringIO

from flask import Blueprint, Response, request

from ...extensions import db
from ...models import Product, Purchase, PurchaseItem, Sale, SaleItem

bp = Blueprint("reports", __name__, url_prefix="/reports")


def _csv_response(name: str, rows: list[list[str]]):
    si = StringIO()
    cw = csv.writer(si)
    cw.writerows(rows)
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={name}"},
    )


@bp.route("/sales.csv")
def sales_csv():
    fro = request.args.get("from")
    to = request.args.get("to")
    q = db.select(Sale).filter(Sale.status == "CONFIRMED")
    if fro:
        q = q.filter(Sale.date >= fro)
    if to:
        q = q.filter(Sale.date <= to)
    rows = db.session.execute(q.order_by(Sale.date.asc())).scalars().all()
    data = [["id", "fecha", "cliente_id", "total"]]
    data += [[s.id, s.date.date().isoformat(), s.customer_id or "", str(s.total)] for s in rows]
    return _csv_response("ventas.csv", data)


@bp.route("/purchases.csv")
def purchases_csv():
    fro = request.args.get("from")
    to = request.args.get("to")
    q = db.select(Purchase).filter(Purchase.status == "CONFIRMED")
    if fro:
        q = q.filter(Purchase.date >= fro)
    if to:
        q = q.filter(Purchase.date <= to)
    rows = db.session.execute(q.order_by(Purchase.date.asc())).scalars().all()
    data = [["id", "fecha", "proveedor_id", "total"]]
    data += [[p.id, p.date.date().isoformat(), p.supplier_id, str(p.total)] for p in rows]
    return _csv_response("compras.csv", data)


@bp.route("/inventory.csv")
def inventory_csv():
    rows = db.session.execute(db.select(Product)).scalars().all()
    data = [["sku", "nombre", "stock", "min_stock", "precio_bruto"]]
    data += [[p.sku, p.name, p.stock, p.min_stock, str(p.price_gross)] for p in rows]
    return _csv_response("inventario.csv", data)
