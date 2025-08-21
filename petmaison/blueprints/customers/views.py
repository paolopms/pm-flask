from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...extensions import db
from ...models import Customer

bp = Blueprint("customers", __name__, url_prefix="/customers", template_folder="../../templates")


@bp.route("")
@login_required
def list_customers():
    q = request.args.get("q", "")
    query = db.select(Customer)
    if q:
        like = f"%{q}%"
        query = query.filter(Customer.name.ilike(like))
    rows = db.session.execute(query.order_by(Customer.created_at.desc())).scalars().all()
    return render_template("customers/list.html", rows=rows, q=q)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_customer():
    if request.method == "POST":
        form = request.form
        c = Customer(
            name=form.get("name", "").strip(),
            rut=form.get("rut") or None,
            email=form.get("email") or None,
            phone=form.get("phone") or None,
            address=form.get("address") or None,
            comuna=form.get("comuna") or None,
        )
        db.session.add(c)
        db.session.commit()
        flash("Cliente creado", "success")
        return redirect(url_for("customers.list_customers"))
    return render_template("customers/form.html", item=None)


@bp.route("/<int:cid>/edit", methods=["GET", "POST"])
@login_required
def edit_customer(cid: int):
    c = db.session.get(Customer, cid)
    if not c:
        flash("No encontrado", "warning")
        return redirect(url_for("customers.list_customers"))
    if request.method == "POST":
        form = request.form
        c.name = form.get("name", c.name)
        c.rut = form.get("rut") or None
        c.email = form.get("email") or None
        c.phone = form.get("phone") or None
        c.address = form.get("address") or None
        c.comuna = form.get("comuna") or None
        db.session.commit()
        flash("Cliente actualizado", "success")
        return redirect(url_for("customers.list_customers"))
    return render_template("customers/form.html", item=c)


@bp.route("/<int:cid>/delete", methods=["POST"])
@login_required
def delete_customer(cid: int):
    c = db.session.get(Customer, cid)
    if c:
        db.session.delete(c)
        db.session.commit()
        flash("Cliente eliminado", "success")
    return redirect(url_for("customers.list_customers"))
