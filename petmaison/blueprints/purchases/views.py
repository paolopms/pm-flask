from __future__ import annotations

from decimal import Decimal
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...extensions import db
from ...models import Product, Purchase, PurchaseItem, StockMovement

bp = Blueprint("purchases", __name__, url_prefix="/purchases", template_folder="../../templates")


@bp.route("")
@login_required
def list_purchases():
    rows = db.session.execute(db.select(Purchase).order_by(Purchase.created_at.desc()).limit(100)).scalars().all()
    return render_template("purchases/list.html", rows=rows)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_purchase():
    if request.method == "POST":
        supplier_id = int(request.form.get("supplier_id", "0") or 0)
        p = Purchase(supplier_id=supplier_id)
        db.session.add(p)
        db.session.commit()
        flash("Compra creada", "success")
        return redirect(url_for("purchases.edit_purchase", pid=p.id))
    return render_template("purchases/create.html")


@bp.route("/<int:pid>", methods=["GET", "POST"])
@login_required
def edit_purchase(pid: int):
    p = db.session.get(Purchase, pid)
    if not p:
        flash("No encontrada", "warning")
        return redirect(url_for("purchases.list_purchases"))

    if request.method == "POST":
        product_id = int(request.form.get("product_id", "0") or 0)
        qty = int(request.form.get("qty", "0") or 0)
        unit_cost_net = Decimal(request.form.get("unit_cost_net", "0") or 0)
        vat_rate = Decimal("0.19")
        line_total = (unit_cost_net * qty) * (1 + vat_rate)
        item = PurchaseItem(
            purchase_id=p.id,
            product_id=product_id,
            qty=qty,
            unit_cost_net=unit_cost_net,
            vat_rate=vat_rate,
            line_total=line_total,
        )
        db.session.add(item)
        db.session.flush()
        # recompute totals
        totals = db.session.execute(
            db.select(
                db.func.coalesce(db.func.sum(PurchaseItem.qty * PurchaseItem.unit_cost_net), 0),
                db.func.coalesce(db.func.sum(PurchaseItem.qty * PurchaseItem.unit_cost_net * PurchaseItem.vat_rate), 0),
            ).filter(PurchaseItem.purchase_id == p.id)
        ).first()
        p.subtotal_net = totals[0]
        p.vat = totals[1]
        p.total = p.subtotal_net + p.vat
        db.session.commit()
        flash("Item agregado", "success")
        return redirect(url_for("purchases.edit_purchase", pid=p.id))

    items = db.session.execute(db.select(PurchaseItem).filter_by(purchase_id=p.id)).scalars().all()
    return render_template("purchases/edit.html", purchase=p, items=items)


@bp.route("/<int:pid>/confirm", methods=["POST"])
@login_required
def confirm_purchase(pid: int):
    p = db.session.get(Purchase, pid)
    if not p:
        flash("No encontrada", "warning")
        return redirect(url_for("purchases.list_purchases"))
    if p.status == "CONFIRMED":
        flash("Ya estaba confirmada", "info")
        return redirect(url_for("purchases.edit_purchase", pid=p.id))

    # Confirm with transaction
    p.status = "CONFIRMED"
    items = db.session.execute(db.select(PurchaseItem).filter_by(purchase_id=p.id)).scalars().all()
    for it in items:
        prod = db.session.get(Product, it.product_id)
        if prod:
            prod.stock += it.qty
            db.session.add(
                StockMovement(
                    product_id=prod.id,
                    type="IN",
                    ref_type="PURCHASE",
                    ref_id=p.id,
                    qty=it.qty,
                    unit_cost_net=it.unit_cost_net,
                )
            )
    db.session.commit()
    flash("Compra confirmada y stock actualizado", "success")
    return redirect(url_for("purchases.edit_purchase", pid=p.id))
