-- DDL de referencia para PostgreSQL
CREATE TYPE role_enum AS ENUM ('admin','vendedor');
CREATE TYPE sale_status AS ENUM ('DRAFT','CONFIRMED','DELIVERED','CANCELLED');
CREATE TYPE purchase_status AS ENUM ('DRAFT','CONFIRMED');
CREATE TYPE order_status AS ENUM ('NEW','PREPARATION','OUT_FOR_DELIVERY','DELIVERED','CANCELLED');
CREATE TYPE payment_method AS ENUM ('EFECTIVO','TRANSFERENCIA','TARJETA');
CREATE TYPE stock_type AS ENUM ('IN','OUT','ADJUSTMENT');
CREATE TYPE stock_ref AS ENUM ('PURCHASE','SALE','ORDER','ADJUSTMENT');

CREATE TABLE users (
  id serial PRIMARY KEY,
  email varchar(255) UNIQUE NOT NULL,
  name varchar(255) NOT NULL,
  password_hash varchar(255) NOT NULL,
  role role_enum NOT NULL,
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now()
);

CREATE TABLE customers (
  id serial PRIMARY KEY,
  name varchar(255) NOT NULL,
  rut varchar(20),
  email varchar(255),
  phone varchar(50),
  address varchar(255),
  comuna varchar(100),
  balance numeric(18,2) NOT NULL DEFAULT 0,
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now()
);

CREATE TABLE suppliers (
  id serial PRIMARY KEY,
  name varchar(255) NOT NULL,
  rut varchar(20),
  contact_name varchar(255),
  phone varchar(50),
  email varchar(255),
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now()
);

CREATE TABLE products (
  id serial PRIMARY KEY,
  sku varchar(64) UNIQUE NOT NULL,
  name varchar(255) NOT NULL,
  brand varchar(255),
  category varchar(255),
  description varchar(1024),
  cost_net numeric(18,2) NOT NULL,
  price_gross numeric(18,2) NOT NULL,
  vat_included boolean NOT NULL DEFAULT true,
  stock int NOT NULL DEFAULT 0,
  min_stock int NOT NULL DEFAULT 0,
  active boolean NOT NULL DEFAULT true,
  image_path varchar(255),
  created_at timestamp NOT NULL DEFAULT now(),
  updated_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_products_sku ON products(sku);
CREATE INDEX ix_products_name ON products(name);
CREATE INDEX ix_products_created_at ON products(created_at);
CREATE INDEX ix_products_updated_at ON products(updated_at);

CREATE TABLE purchases (
  id serial PRIMARY KEY,
  supplier_id int NOT NULL REFERENCES suppliers(id),
  date timestamp NOT NULL DEFAULT now(),
  notes varchar(1024),
  status purchase_status NOT NULL DEFAULT 'DRAFT',
  subtotal_net numeric(18,2) NOT NULL DEFAULT 0,
  vat numeric(18,2) NOT NULL DEFAULT 0,
  total numeric(18,2) NOT NULL DEFAULT 0,
  created_at timestamp NOT NULL DEFAULT now()
);

CREATE TABLE purchase_items (
  id serial PRIMARY KEY,
  purchase_id int NOT NULL REFERENCES purchases(id),
  product_id int NOT NULL REFERENCES products(id),
  qty int NOT NULL,
  unit_cost_net numeric(18,2) NOT NULL,
  vat_rate numeric(5,2) NOT NULL DEFAULT 0.19,
  line_total numeric(18,2) NOT NULL
);

CREATE TABLE sales (
  id serial PRIMARY KEY,
  customer_id int REFERENCES customers(id),
  user_id int NOT NULL REFERENCES users(id),
  date timestamp NOT NULL DEFAULT now(),
  status sale_status NOT NULL DEFAULT 'DRAFT',
  subtotal_net numeric(18,2) NOT NULL DEFAULT 0,
  discount numeric(18,2) NOT NULL DEFAULT 0,
  vat numeric(18,2) NOT NULL DEFAULT 0,
  total numeric(18,2) NOT NULL DEFAULT 0,
  payment_method payment_method NOT NULL,
  created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_sales_date ON sales(date);

CREATE TABLE sale_items (
  id serial PRIMARY KEY,
  sale_id int NOT NULL REFERENCES sales(id),
  product_id int NOT NULL REFERENCES products(id),
  qty int NOT NULL,
  unit_price_net numeric(18,2) NOT NULL,
  discount numeric(18,2) NOT NULL DEFAULT 0,
  vat_rate numeric(5,2) NOT NULL DEFAULT 0.19,
  line_total numeric(18,2) NOT NULL
);

CREATE TABLE orders (
  id serial PRIMARY KEY,
  customer_id int NOT NULL REFERENCES customers(id),
  address varchar(255) NOT NULL,
  time_window varchar(100),
  notes varchar(1024),
  status order_status NOT NULL DEFAULT 'NEW',
  sale_id int REFERENCES sales(id),
  created_at timestamp NOT NULL DEFAULT now()
);

CREATE TABLE stock_movements (
  id serial PRIMARY KEY,
  product_id int NOT NULL REFERENCES products(id),
  type stock_type NOT NULL,
  ref_type stock_ref NOT NULL,
  ref_id int,
  qty int NOT NULL,
  unit_cost_net numeric(18,2),
  created_at timestamp NOT NULL DEFAULT now()
);
CREATE INDEX ix_stock_movements_product_id ON stock_movements(product_id);
CREATE INDEX ix_stock_movements_created_at ON stock_movements(created_at);
