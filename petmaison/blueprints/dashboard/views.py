from __future__ import annotations

from datetime import datetime, timedelta

from flask import Blueprint, render_template

from ...extensions import db
from ...models import Product, Sale, SaleItem

bp = Blueprint("dashboard", __name__, url_prefix="/", template_folder="../../templates")


@bp.route("")
def index():
    today = datetime.utcnow().date()
    start_month = today.replace(day=1)

    sales_today = db.session.execute(
        db.select(db.func.coalesce(db.func.sum(Sale.total), 0)).filter(
            db.func.date(Sale.date) == today, Sale.status == "CONFIRMED"
        )
    ).scalar() or 0

    sales_month = db.session.execute(
        db.select(db.func.coalesce(db.func.sum(Sale.total), 0)).filter(
            Sale.date >= start_month, Sale.status == "CONFIRMED"
        )
    ).scalar() or 0

    sales_count = db.session.execute(
        db.select(db.func.count(Sale.id)).filter(Sale.date >= start_month, Sale.status == "CONFIRMED")
    ).scalar() or 1

    ticket_prom = (sales_month or 0) / max(sales_count, 1)

    top_units = db.session.execute(
        db.select(Product.name, db.func.sum(SaleItem.qty).label("u")).join(SaleItem.product).join(SaleItem.sale).filter(
            Sale.status == "CONFIRMED", Sale.date >= start_month
        ).group_by(Product.id).order_by(db.text("u desc")).limit(5)
    ).all()

    return render_template(
        "dashboard/index.html",
        sales_today=sales_today,
        sales_month=sales_month,
        ticket_prom=ticket_prom,
        top_units=top_units,
    )
