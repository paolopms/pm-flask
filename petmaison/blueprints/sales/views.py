from __future__ import annotations

from decimal import Decimal
from io import BytesIO

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ...extensions import db
from ...models import Product, Sale, SaleItem, StockMovement

bp = Blueprint("sales", __name__, url_prefix="/sales", template_folder="../../templates")


@bp.route("")
@login_required
def list_sales():
    rows = db.session.execute(db.select(Sale).order_by(Sale.created_at.desc()).limit(100)).scalars().all()
    return render_template("sales/list.html", rows=rows)


@bp.route("/pos", methods=["GET", "POST"])
@login_required
def pos():
    if request.method == "POST":
        sale_id = request.form.get("sale_id")
        if sale_id:
            sale = db.session.get(Sale, int(sale_id))
        else:
            sale = Sale(user_id=current_user.id, payment_method="EFECTIVO")
            db.session.add(sale)
            db.session.flush()
        product_id = int(request.form.get("product_id", "0") or 0)
        qty = int(request.form.get("qty", "1") or 1)
        unit_price_net = Decimal(request.form.get("unit_price_net", "0") or 0)
        discount = Decimal(request.form.get("discount", "0") or 0)
        vat_rate = Decimal("0.19")
        line_total = (unit_price_net * qty - discount) * (1 + vat_rate)
        db.session.add(
            SaleItem(
                sale_id=sale.id,
                product_id=product_id,
                qty=qty,
                unit_price_net=unit_price_net,
                discount=discount,
                vat_rate=vat_rate,
                line_total=line_total,
            )
        )
        # recompute totals
        totals = db.session.execute(
            db.select(
                db.func.coalesce(db.func.sum(SaleItem.qty * SaleItem.unit_price_net - SaleItem.discount), 0),
                db.func.coalesce(
                    db.func.sum((SaleItem.qty * SaleItem.unit_price_net - SaleItem.discount) * SaleItem.vat_rate),
                    0,
                ),
            ).filter(SaleItem.sale_id == sale.id)
        ).first()
        sale.subtotal_net = totals[0]
        sale.vat = totals[1]
        sale.total = sale.subtotal_net + sale.vat
        db.session.commit()
        flash("Ítem agregado", "success")
        return redirect(url_for("sales.pos", sale_id=sale.id))

    sale_id = request.args.get("sale_id")
    sale = db.session.get(Sale, int(sale_id)) if sale_id else None
    items = (
        db.session.execute(db.select(SaleItem).filter_by(sale_id=sale.id)).scalars().all() if sale else []
    )
    return render_template("sales/pos.html", sale=sale, items=items)


@bp.route("/<int:sid>/confirm", methods=["POST"])
@login_required
def confirm_sale(sid: int):
    sale = db.session.get(Sale, sid)
    if not sale:
        flash("No encontrada", "warning")
        return redirect(url_for("sales.list_sales"))
    if sale.status == "CONFIRMED":
        flash("Ya confirmada", "info")
        return redirect(url_for("sales.pos", sale_id=sale.id))

    sale.status = "CONFIRMED"
    items = db.session.execute(db.select(SaleItem).filter_by(sale_id=sale.id)).scalars().all()
    for it in items:
        prod = db.session.get(Product, it.product_id)
        if prod:
            if prod.stock < it.qty:
                flash(f"Stock insuficiente para {prod.name}", "danger")
                return redirect(url_for("sales.pos", sale_id=sale.id))
            prod.stock -= it.qty
            db.session.add(
                StockMovement(
                    product_id=prod.id,
                    type="OUT",
                    ref_type="SALE",
                    ref_id=sale.id,
                    qty=it.qty,
                    unit_cost_net=prod.cost_net,
                )
            )
    db.session.commit()
    flash("Venta confirmada y stock actualizado", "success")
    return redirect(url_for("sales.pos", sale_id=sale.id))


@bp.route("/<int:sid>/ticket")
@login_required
def ticket(sid: int):
    # Placeholder simple HTML -> PDF podría integrarse con xhtml2pdf/WeasyPrint
    sale = db.session.get(Sale, sid)
    return render_template("sales/ticket.html", sale=sale)
