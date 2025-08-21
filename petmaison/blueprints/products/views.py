from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from flask import Blueprint, flash, redirect, render_template, request, url_for, current_app
from flask_login import login_required

from ...extensions import db
from ...models import Product

bp = Blueprint("products", __name__, url_prefix="/products", template_folder="../../templates")


@bp.route("")
@login_required
def list_products():
    q = request.args.get("q", "")
    query = db.select(Product)
    if q:
        like = f"%{q}%"
        query = query.filter(db.or_(Product.name.ilike(like), Product.sku.ilike(like)))
    rows = db.session.execute(query.order_by(Product.created_at.desc())).scalars().all()
    return render_template("products/list.html", rows=rows, q=q)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_product():
    if request.method == "POST":
        form = request.form
        image_path = None
        if "image" in request.files and request.files["image"].filename:
            f = request.files["image"]
            filename = f"{uuid4().hex}_{f.filename}"
            dest = current_app.config["MEDIA_ROOT"]
            f.save(f"{dest}/{filename}")
            image_path = f"/media/{filename}"
        p = Product(
            sku=form.get("sku", "").strip(),
            name=form.get("name", "").strip(),
            brand=form.get("brand") or None,
            category=form.get("category") or None,
            description=form.get("description") or None,
            cost_net=Decimal(form.get("cost_net", "0") or 0),
            price_gross=Decimal(form.get("price_gross", "0") or 0),
            vat_included=bool(form.get("vat_included")),
            stock=int(form.get("stock", "0") or 0),
            min_stock=int(form.get("min_stock", "0") or 0),
            active=bool(form.get("active", True)),
            image_path=image_path,
        )
        db.session.add(p)
        db.session.commit()
        flash("Producto creado", "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/form.html", item=None)


@bp.route("/<int:pid>/edit", methods=["GET", "POST"])
@login_required
def edit_product(pid: int):
    p = db.session.get(Product, pid)
    if not p:
        flash("Producto no encontrado", "warning")
        return redirect(url_for("products.list_products"))
    if request.method == "POST":
        form = request.form
        p.sku = form.get("sku", p.sku)
        p.name = form.get("name", p.name)
        p.brand = form.get("brand") or None
        p.category = form.get("category") or None
        p.description = form.get("description") or None
        p.cost_net = Decimal(form.get("cost_net", p.cost_net) or 0)
        p.price_gross = Decimal(form.get("price_gross", p.price_gross) or 0)
        p.vat_included = bool(form.get("vat_included"))
        p.stock = int(form.get("stock", p.stock) or 0)
        p.min_stock = int(form.get("min_stock", p.min_stock) or 0)
        p.active = bool(form.get("active", p.active))
        db.session.commit()
        flash("Producto actualizado", "success")
        return redirect(url_for("products.list_products"))
    return render_template("products/form.html", item=p)


@bp.route("/<int:pid>/delete", methods=["POST"])
@login_required
def delete_product(pid: int):
    p = db.session.get(Product, pid)
    if p:
        db.session.delete(p)
        db.session.commit()
        flash("Producto eliminado", "success")
    return redirect(url_for("products.list_products"))
