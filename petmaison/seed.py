from __future__ import annotations

import random
from datetime import datetime, timedelta
from decimal import Decimal

from flask import current_app
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

from .extensions import db
from .models import (
    Customer,
    Order,
    Product,
    Purchase,
    PurchaseItem,
    Sale,
    SaleItem,
    Supplier,
    User,
)


@with_appcontext
def run_seed() -> None:
    random.seed(42)
    db.drop_all()
    db.create_all()

    # Users
    admin = User(
        email="admin@petmaison.cl",
        name="Admin",
        password_hash=generate_password_hash("PetMaison!2025"),
        role="admin",
    )
    vend = User(
        email="vendedor@petmaison.cl",
        name="Vendedor",
        password_hash=generate_password_hash("PetMaison!2025"),
        role="vendedor",
    )
    db.session.add_all([admin, vend])

    # Customers
    customers: list[Customer] = []
    for i in range(5):
        customers.append(Customer(name=f"Cliente {i+1}"))
    db.session.add_all(customers)

    # Suppliers
    suppliers: list[Supplier] = []
    for i in range(3):
        suppliers.append(Supplier(name=f"Proveedor {i+1}"))
    db.session.add_all(suppliers)

    # Products
    products: list[Product] = []
    for i in range(20):
        products.append(
            Product(
                sku=f"SKU{i+1:03}",
                name=f"Producto {i+1}",
                brand="MarcaX",
                category="General",
                cost_net=Decimal("1000") + i,
                price_gross=Decimal("1190") + i,
                vat_included=True,
                stock=10,
                min_stock=2,
                active=True,
            )
        )
    db.session.add_all(products)

    db.session.commit()

    # Purchases (confirmadas)
    for i in range(3):
        p = Purchase(supplier_id=suppliers[i % len(suppliers)].id, status="CONFIRMED")
        db.session.add(p)
        db.session.flush()
        for j in range(3):
            prod = products[(i * 3 + j) % len(products)]
            qty = 5
            unit_cost = prod.cost_net
            db.session.add(
                PurchaseItem(
                    purchase_id=p.id,
                    product_id=prod.id,
                    qty=qty,
                    unit_cost_net=unit_cost,
                    vat_rate=Decimal("0.19"),
                    line_total=(unit_cost * qty) * Decimal("1.19"),
                )
            )
            prod.stock += qty
        p.subtotal_net = Decimal("5000")
        p.vat = Decimal("950")
        p.total = Decimal("5950")
    db.session.commit()

    # Sales (confirmadas)
    for i in range(10):
        s = Sale(
            user_id=admin.id,
            customer_id=customers[i % len(customers)].id,
            status="CONFIRMED",
            payment_method="EFECTIVO",
            date=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
        )
        db.session.add(s)
        db.session.flush()
        for j in range(2):
            prod = products[(i * 2 + j) % len(products)]
            qty = 1
            db.session.add(
                SaleItem(
                    sale_id=s.id,
                    product_id=prod.id,
                    qty=qty,
                    unit_price_net=prod.cost_net * Decimal("1.2"),
                    discount=Decimal("0"),
                    vat_rate=Decimal("0.19"),
                    line_total=(prod.cost_net * Decimal("1.2")) * Decimal("1.19"),
                )
            )
            prod.stock = max(prod.stock - qty, 0)
        s.subtotal_net = Decimal("2400")
        s.vat = Decimal("456")
        s.total = Decimal("2856")
    db.session.commit()

    # Orders
    for i in range(5):
        db.session.add(
            Order(
                customer_id=customers[i % len(customers)].id,
                address=f"Calle {i+1}",
                status="NEW",
            )
        )
    db.session.commit()

    print("Seed completado.")
