from __future__ import annotations

from datetime import datetime

from flask import Blueprint, render_template, request

from ...extensions import db
from ...models import Product, StockMovement

bp = Blueprint("inventory", __name__, url_prefix="/inventory", template_folder="../../templates")


@bp.route("/kardex/<int:product_id>")
def kardex(product_id: int):
    fro = request.args.get("from")
    to = request.args.get("to")
    q = db.select(StockMovement).filter(StockMovement.product_id == product_id)
    if fro:
        q = q.filter(StockMovement.created_at >= fro)
    if to:
        q = q.filter(StockMovement.created_at <= to)
    rows = db.session.execute(q.order_by(StockMovement.created_at.asc())).scalars().all()
    product = db.session.get(Product, product_id)
    return render_template("inventory/kardex.html", rows=rows, product=product)
