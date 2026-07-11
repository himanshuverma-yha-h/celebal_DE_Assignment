import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta
import os

fake = Faker()

random.seed(42)
Faker.seed(42)

# Create raw data directory
os.makedirs("data/raw", exist_ok=True)


# -----------------------------
# GENERATE CUSTOMERS
# -----------------------------

customers = []

customer_types = ["REGULAR", "PREMIUM", "VIP"]

for i in range(1, 601):

    customer_id = i
    customer_name = fake.name()
    email = fake.email()

    registration_date = fake.date_between(
        start_date="-3y",
        end_date="-1y"
    )

    customer_type = random.choice(customer_types)

    customers.append([
        customer_id,
        customer_name,
        email,
        registration_date,
        customer_type
    ])


customers_df = pd.DataFrame(
    customers,
    columns=[
        "customer_id",
        "customer_name",
        "email",
        "registration_date",
        "customer_type"
    ]
)


# Introduce 2% invalid emails

invalid_email_count = int(len(customers_df) * 0.02)

invalid_indices = random.sample(
    list(customers_df.index),
    invalid_email_count
)

for index in invalid_indices:

    invalid_email_types = [
        "invalidemail.com",
        "customer@",
        "wrongemail",
        "user.com"
    ]

    customers_df.loc[index, "email"] = random.choice(
        invalid_email_types
    )


customers_df.to_csv(
    "data/raw/customers.csv",
    index=False
)


# -----------------------------
# GENERATE PRODUCTS
# -----------------------------

products = []

categories = {
    "Electronics": [
        "Laptop",
        "Smartphone",
        "Headphones",
        "Keyboard",
        "Mouse"
    ],

    "Clothing": [
        "T Shirt",
        "Jeans",
        "Jacket",
        "Sweater",
        "Shoes"
    ],

    "Home": [
        "Chair",
        "Table",
        "Lamp",
        "Curtain",
        "Pillow"
    ],

    "Books": [
        "Python Book",
        "SQL Book",
        "Data Engineering Book",
        "Machine Learning Book",
        "Cloud Computing Book"
    ]
}


for i in range(1, 501):

    category = random.choice(list(categories.keys()))

    product_name = random.choice(
        categories[category]
    )

    subcategory = product_name

    cost_price = round(
        random.uniform(100, 50000),
        2
    )

    # Introduce messy product names

    if random.random() < 0.10:

        messy_names = [
            "  " + product_name,
            product_name + "  ",
            product_name.upper(),
            product_name.lower(),
            " " + product_name.upper() + " "
        ]

        product_name = random.choice(messy_names)

    products.append([
        i,
        product_name,
        category,
        subcategory,
        cost_price
    ])


products_df = pd.DataFrame(
    products,
    columns=[
        "product_id",
        "product_name",
        "category",
        "subcategory",
        "cost_price"
    ]
)


products_df.to_csv(
    "data/raw/products.csv",
    index=False
)


# -----------------------------
# GENERATE ORDERS
# -----------------------------

orders = []

statuses = [
    "PLACED",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
    "RETURNED"
]

regions = [
    "NORTH",
    "SOUTH",
    "EAST",
    "WEST"
]


for i in range(1, 1201):

    customer_id = random.randint(1, 600)

    order_date = fake.date_time_between(
        start_date="-2y",
        end_date="now"
    )

    status = random.choice(statuses)

    region_code = random.choice(regions)

    # 5% NULL customer IDs

    if random.random() < 0.05:
        customer_id = None

    # Some wrong date formats

    if random.random() < 0.05:

        order_date = order_date.strftime(
            "%d-%m-%Y"
        )

    else:

        order_date = order_date.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    orders.append([
        i,
        customer_id,
        order_date,
        status,
        region_code
    ])


orders_df = pd.DataFrame(
    orders,
    columns=[
        "order_id",
        "customer_id",
        "order_date",
        "status",
        "region_code"
    ]
)


orders_df.to_csv(
    "data/raw/orders.csv",
    index=False
)


# -----------------------------
# GENERATE ORDER ITEMS
# -----------------------------

order_items = []

for i in range(1, 3001):

    order_id = random.randint(1, 1200)

    product_id = random.randint(1, 500)

    quantity = random.randint(1, 5)

    unit_price = round(
        random.uniform(100, 60000),
        2
    )

    discount_percent = random.randint(0, 40)

    # 3% negative quantity for returns

    if random.random() < 0.03:

        quantity = -quantity

    order_items.append([
        i,
        order_id,
        product_id,
        quantity,
        unit_price,
        discount_percent
    ])


order_items_df = pd.DataFrame(
    order_items,
    columns=[
        "item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
        "discount_percent"
    ]
)


order_items_df.to_csv(
    "data/raw/order_items.csv",
    index=False
)


# -----------------------------
# SUMMARY
# -----------------------------

print("\nDATA GENERATION COMPLETED\n")

print("Customers:", len(customers_df))
print("Products:", len(products_df))
print("Orders:", len(orders_df))
print("Order Items:", len(order_items_df))

print("\nRaw CSV files created in data/raw/")