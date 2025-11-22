DROP TABLE IF EXISTS products;
CREATE TABLE products (
	sku INTEGER,
	brand VARCHAR(25),
	description VARCHAR(100),
	unit_price FLOAT,
	qty_in_stock INTEGER,
	PRIMARY KEY (sku)
);