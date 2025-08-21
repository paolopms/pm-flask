from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from flask_login import UserMixin
from sqlalchemy import CheckConstraint, Enum, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .extensions import db


ROLE_ENUM = ("admin", "vendedor")
SALE_STATUS = ("DRAFT", "CONFIRMED", "DELIVERED", "CANCELLED")
PURCHASE_STATUS = ("DRAFT", "CONFIRMED")
ORDER_STATUS = ("NEW", "PREPARATION", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED")
PAYMENT_METHOD = ("EFECTIVO", "TRANSFERENCIA", "TARJETA")
STOCK_TYPE = ("IN", "OUT", "ADJUSTMENT")
STOCK_REF = ("PURCHASE", "SALE", "ORDER", "ADJUSTMENT")


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class User(db.Model, UserMixin, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(db.Enum(*ROLE_ENUM, name="role_enum"), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    def __repr__(self) -> str:
        return f"<User {self.id} {self.email} {self.role}>"


class Customer(db.Model, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    rut: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    address: Mapped[str | None] = mapped_column(String(255))
    comuna: Mapped[str | None] = mapped_column(String(100))
    balance: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), default=Decimal("0"), nullable=False)

    def __repr__(self) -> str:
        return f"<Customer {self.id} {self.name}>"


class Supplier(db.Model, TimestampMixin):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    rut: Mapped[str | None] = mapped_column(String(20))
    contact_name: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"<Supplier {self.id} {self.name}>"


class Product(db.Model, TimestampMixin):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_sku", "sku", unique=True),
        Index("ix_products_name", "name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    brand: Mapped[str | None] = mapped_column(String(255))
    category: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(String(1024))
    cost_net: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), nullable=False)
    price_gross: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), nullable=False)
    vat_included: Mapped[bool] = mapped_column(default=True, nullable=False)
    stock: Mapped[int] = mapped_column(default=0, nullable=False)
    min_stock: Mapped[int] = mapped_column(default=0, nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    image_path: Mapped[str | None] = mapped_column(String(255))

    def __repr__(self) -> str:
        return f"<Product {self.id} {self.sku} {self.name}>"


class Purchase(db.Model, TimestampMixin):
    __tablename__ = "purchases"

    id: Mapped[int] = mapped_column(primary_key=True)
    supplier_id: Mapped[int] = mapped_column(ForeignKey("suppliers.id"), nullable=False, index=True)
    supplier = relationship("Supplier")
    date: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(db.Enum(*PURCHASE_STATUS, name="purchase_status"), default="DRAFT", nullable=False)
    subtotal_net: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), default=Decimal("0"), nullable=False)
    vat: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), default=Decimal("0"), nullable=False)
    total: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), default=Decimal("0"), nullable=False)


class PurchaseItem(db.Model):
    __tablename__ = "purchase_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    purchase_id: Mapped[int] = mapped_column(ForeignKey("purchases.id"), nullable=False, index=True)
    purchase = relationship("Purchase", backref="items")
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    product = relationship("Product")
    qty: Mapped[int] = mapped_column(nullable=False)
    unit_cost_net: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), nullable=False)
    vat_rate: Mapped[Decimal] = mapped_column(db.Numeric(5, 2), default=Decimal("0.19"), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), nullable=False)


class Sale(db.Model, TimestampMixin):
    __tablename__ = "sales"
    __table_args__ = (Index("ix_sales_date", "date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int | None] = mapped_column(ForeignKey("customers.id"))
    customer = relationship("Customer")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user = relationship("User")
    date: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(db.Enum(*SALE_STATUS, name="sale_status"), default="DRAFT", nullable=False)
    subtotal_net: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), default=Decimal("0"), nullable=False)
    discount: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), default=Decimal("0"), nullable=False)
    vat: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), default=Decimal("0"), nullable=False)
    total: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), default=Decimal("0"), nullable=False)
    payment_method: Mapped[str] = mapped_column(db.Enum(*PAYMENT_METHOD, name="payment_method"), nullable=False)


class SaleItem(db.Model):
    __tablename__ = "sale_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"), nullable=False, index=True)
    sale = relationship("Sale", backref="items")
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    product = relationship("Product")
    qty: Mapped[int] = mapped_column(nullable=False)
    unit_price_net: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), default=Decimal("0"), nullable=False)
    vat_rate: Mapped[Decimal] = mapped_column(db.Numeric(5, 2), default=Decimal("0.19"), nullable=False)
    line_total: Mapped[Decimal] = mapped_column(db.Numeric(18, 2), nullable=False)


class Order(db.Model, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)
    customer = relationship("Customer")
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    time_window: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(db.Enum(*ORDER_STATUS, name="order_status"), default="NEW", nullable=False)
    sale_id: Mapped[int | None] = mapped_column(ForeignKey("sales.id"))


class StockMovement(db.Model):
    __tablename__ = "stock_movements"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False, index=True)
    product = relationship("Product")
    type: Mapped[str] = mapped_column(db.Enum(*STOCK_TYPE, name="stock_type"), nullable=False)
    ref_type: Mapped[str] = mapped_column(db.Enum(*STOCK_REF, name="stock_ref"), nullable=False)
    ref_id: Mapped[int | None]
    qty: Mapped[int] = mapped_column(nullable=False)
    unit_cost_net: Mapped[Decimal | None] = mapped_column(db.Numeric(18, 2))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False, index=True)


Index("ix_products_created_at", Product.created_at)
Index("ix_products_updated_at", Product.updated_at)
