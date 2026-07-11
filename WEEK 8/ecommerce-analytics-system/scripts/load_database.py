import sqlite3
import pandas as pd
import os


DATABASE_PATH = "database/ecommerce.db"
SCHEMA_PATH = "sql/schema.sql"
CLEAN_DATA_PATH = "data/cleaned"


os.makedirs("database", exist_ok=True)


# --------------------------------
# CONNECT TO DATABASE
# --------------------------------

connection = sqlite3.connect(DATABASE_PATH)

connection.execute("PRAGMA foreign_keys = ON")

cursor = connection.cursor()


# --------------------------------
# CREATE DATABASE SCHEMA
# --------------------------------

with open(SCHEMA_PATH, "r") as file:
    schema_sql = file.read()

cursor.executescript(schema_sql)

print("\nDatabase schema created successfully")


# --------------------------------
# LOAD CLEANED CSV FILES
# --------------------------------

customers_df = pd.read_csv(
    f"{CLEAN_DATA_PATH}/customers_clean.csv"
)

products_df = pd.read_csv(
    f"{CLEAN_DATA_PATH}/products_clean.csv"
)

orders_df = pd.read_csv(
    f"{CLEAN_DATA_PATH}/orders_clean.csv"
)

order_items_df = pd.read_csv(
    f"{CLEAN_DATA_PATH}/order_items_clean.csv"
)


# --------------------------------
# INSERT CUSTOMERS
# --------------------------------

customers_df.to_sql(
    "customers",
    connection,
    if_exists="append",
    index=False
)

print(
    "Customers loaded:",
    len(customers_df)
)


# --------------------------------
# INSERT PRODUCTS
# --------------------------------

products_df.to_sql(
    "products",
    connection,
    if_exists="append",
    index=False
)

print(
    "Products loaded:",
    len(products_df)
)


# --------------------------------
# INSERT ORDERS
# --------------------------------

orders_df.to_sql(
    "orders",
    connection,
    if_exists="append",
    index=False
)

print(
    "Orders loaded:",
    len(orders_df)
)


# --------------------------------
# INSERT ORDER ITEMS
# --------------------------------

order_items_df.to_sql(
    "order_items",
    connection,
    if_exists="append",
    index=False
)

print(
    "Order Items loaded:",
    len(order_items_df)
)


# --------------------------------
# COMMIT DATA
# --------------------------------

connection.commit()


# --------------------------------
# VERIFY ROW COUNTS
# --------------------------------

print("\nDATABASE ROW COUNTS")

tables = [
    "customers",
    "products",
    "orders",
    "order_items"
]

for table in tables:

    cursor.execute(
        f"SELECT COUNT(*) FROM {table}"
    )

    count = cursor.fetchone()[0]

    print(
        f"{table}: {count}"
    )


# --------------------------------
# VERIFY FOREIGN KEY RELATIONSHIPS
# --------------------------------

cursor.execute("""
    SELECT COUNT(*)
    FROM order_items oi
    LEFT JOIN orders o
        ON oi.order_id = o.order_id
    WHERE o.order_id IS NULL
""")

invalid_order_references = cursor.fetchone()[0]


cursor.execute("""
    SELECT COUNT(*)
    FROM order_items oi
    LEFT JOIN products p
        ON oi.product_id = p.product_id
    WHERE p.product_id IS NULL
""")

invalid_product_references = cursor.fetchone()[0]


cursor.execute("""
    SELECT COUNT(*)
    FROM orders o
    LEFT JOIN customers c
        ON o.customer_id = c.customer_id
    WHERE c.customer_id IS NULL
""")

invalid_customer_references = cursor.fetchone()[0]


print("\nREFERENTIAL INTEGRITY CHECK")

print(
    "Invalid customer references:",
    invalid_customer_references
)

print(
    "Invalid order references:",
    invalid_order_references
)

print(
    "Invalid product references:",
    invalid_product_references
)


# --------------------------------
# FOREIGN KEY CHECK
# --------------------------------

cursor.execute(
    "PRAGMA foreign_key_check"
)

foreign_key_errors = cursor.fetchall()

print(
    "\nSQLite foreign key errors:",
    len(foreign_key_errors)
)


# --------------------------------
# CLOSE CONNECTION
# --------------------------------

connection.close()

print(
    "\nDATABASE LOADING COMPLETED SUCCESSFULLY"
)