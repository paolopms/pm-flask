from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required

from ...extensions import db
from ...models import Supplier

bp = Blueprint("suppliers", __name__, url_prefix="/suppliers", template_folder="../../templates")


@bp.route("")
@login_required
def list_suppliers():
    rows = db.session.execute(db.select(Supplier).order_by(Supplier.created_at.desc())).scalars().all()
    return render_template("suppliers/list.html", rows=rows)


@bp.route("/create", methods=["GET", "POST"])
@login_required
def create_supplier():
    if request.method == "POST":
        s = Supplier(name=request.form.get("name", "").strip())
        db.session.add(s)
        db.session.commit()
        flash("Proveedor creado", "success")
        return redirect(url_for("suppliers.list_suppliers"))
    return render_template("suppliers/form.html", item=None)
