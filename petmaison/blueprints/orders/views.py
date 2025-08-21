from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...extensions import db
from ...models import Order, Sale

bp = Blueprint("orders", __name__, url_prefix="/orders", template_folder="../../templates")


@bp.route("")
@login_required
def list_orders():
    rows = db.session.execute(db.select(Order).order_by(Order.created_at.desc()).limit(200)).scalars().all()
    return render_template("orders/list.html", rows=rows)


@bp.route("/<int:oid>/status", methods=["POST"])
@login_required
def update_status(oid: int):
    o = db.session.get(Order, oid)
    if not o:
        flash("No encontrado", "warning")
        return redirect(url_for("orders.list_orders"))
    new_status = request.form.get("status")
    if new_status not in ["NEW","PREPARATION","OUT_FOR_DELIVERY","DELIVERED","CANCELLED"]:
        flash("Estado inválido", "danger")
        return redirect(url_for("orders.list_orders"))
    o.status = new_status
    db.session.commit()
    flash("Estado actualizado", "success")
    return redirect(url_for("orders.list_orders"))


@bp.route("/<int:oid>/link_sale", methods=["POST"])
@login_required
def link_sale(oid: int):
    o = db.session.get(Order, oid)
    sid = int(request.form.get("sale_id", "0") or 0)
    sale = db.session.get(Sale, sid)
    if not o or not sale:
        flash("Pedido o venta inexistente", "warning")
        return redirect(url_for("orders.list_orders"))
    o.sale_id = sale.id
    db.session.commit()
    flash("Pedido vinculado a venta", "success")
    return redirect(url_for("orders.list_orders"))
