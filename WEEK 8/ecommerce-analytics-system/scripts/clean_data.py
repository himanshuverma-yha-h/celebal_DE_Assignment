import pandas as pd
import os

RAW_DATA_PATH = "data/raw"
CLEAN_DATA_PATH = "data/cleaned"
OUTPUT_PATH = "output"

os.makedirs(CLEAN_DATA_PATH, exist_ok=True)
os.makedirs(OUTPUT_PATH, exist_ok=True)

issues = []


# --------------------------------
# LOAD RAW DATA
# --------------------------------

customers_df = pd.read_csv(
    f"{RAW_DATA_PATH}/customers.csv"
)

products_df = pd.read_csv(
    f"{RAW_DATA_PATH}/products.csv"
)

orders_df = pd.read_csv(
    f"{RAW_DATA_PATH}/orders.csv"
)

order_items_df = pd.read_csv(
    f"{RAW_DATA_PATH}/order_items.csv"
)


# --------------------------------
# CLEAN ORDERS
# --------------------------------

def clean_orders(df):

    print("\nCleaning orders...")

    df = df.copy()

    null_customer_count = df["customer_id"].isna().sum()

    issues.append(
        f"Orders with NULL customer_id: {null_customer_count}"
    )

    # Remove orders with missing customer ID

    df = df.dropna(subset=["customer_id"])

    # Convert customer_id back to integer

    df["customer_id"] = df["customer_id"].astype(int)

    # Fix mixed date formats

    parsed_dates = pd.to_datetime(
        df["order_date"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    wrong_format_mask = parsed_dates.isna()

    wrong_date_count = wrong_format_mask.sum()

    issues.append(
        f"Orders with wrong date format: {wrong_date_count}"
    )

    parsed_dates.loc[wrong_format_mask] = pd.to_datetime(
        df.loc[wrong_format_mask, "order_date"],
        format="%d-%m-%Y",
        errors="coerce"
    )

    invalid_date_count = parsed_dates.isna().sum()

    issues.append(
        f"Orders with invalid dates after parsing: {invalid_date_count}"
    )

    df["order_date"] = parsed_dates

    # Remove dates that still cannot be parsed

    df = df.dropna(subset=["order_date"])

    # Remove duplicate orders

    duplicate_count = df.duplicated().sum()

    issues.append(
        f"Duplicate orders removed: {duplicate_count}"
    )

    df = df.drop_duplicates()

    return df


# --------------------------------
# CLEAN PRODUCTS
# --------------------------------

def clean_products(df):

    print("Cleaning products...")

    df = df.copy()

    messy_product_count = (
        df["product_name"]
        != df["product_name"].str.strip().str.title()
    ).sum()

    issues.append(
        f"Product names normalized: {messy_product_count}"
    )

    df["product_name"] = (
        df["product_name"]
        .str.strip()
        .str.title()
    )

    duplicate_count = df.duplicated().sum()

    issues.append(
        f"Duplicate products removed: {duplicate_count}"
    )

    df = df.drop_duplicates()

    return df


# --------------------------------
# VALIDATE EMAILS
# --------------------------------

def validate_emails(df):

    print("Validating emails...")

    email_pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    invalid_email_mask = ~df["email"].str.match(
        email_pattern,
        na=False
    )

    invalid_customer_ids = df.loc[
        invalid_email_mask,
        "customer_id"
    ].tolist()

    issues.append(
        f"Invalid email count: {len(invalid_customer_ids)}"
    )

    issues.append(
        f"Customers with invalid emails: {invalid_customer_ids}"
    )

    return invalid_customer_ids


# --------------------------------
# CLEAN CUSTOMERS
# --------------------------------

def clean_customers(df):

    print("Cleaning customers...")

    df = df.copy()

    duplicate_count = df.duplicated().sum()

    issues.append(
        f"Duplicate customers removed: {duplicate_count}"
    )

    df = df.drop_duplicates()

    df["customer_name"] = (
        df["customer_name"]
        .str.strip()
        .str.title()
    )

    df["customer_type"] = (
        df["customer_type"]
        .str.strip()
        .str.upper()
    )

    df["registration_date"] = pd.to_datetime(
        df["registration_date"],
        errors="coerce"
    )

    invalid_email_ids = validate_emails(df)

    # Remove invalid email customers

    df = df[
        ~df["customer_id"].isin(invalid_email_ids)
    ]

    return df


# --------------------------------
# CLEAN ORDER ITEMS
# --------------------------------

def clean_order_items(df):

    print("Cleaning order items...")

    df = df.copy()

    duplicate_count = df.duplicated().sum()

    issues.append(
        f"Duplicate order items removed: {duplicate_count}"
    )

    df = df.drop_duplicates()

    negative_quantity_count = (
        df["quantity"] < 0
    ).sum()

    issues.append(
        f"Negative quantity records found: {negative_quantity_count}"
    )

    invalid_discount_count = (
        (df["discount_percent"] < 0)
        | (df["discount_percent"] > 100)
    ).sum()

    issues.append(
        f"Invalid discount records found: {invalid_discount_count}"
    )

    # Remove invalid discounts

    df = df[
        (df["discount_percent"] >= 0)
        & (df["discount_percent"] <= 100)
    ]

    return df


# --------------------------------
# CHECK REFERENTIAL INTEGRITY
# --------------------------------

def check_referential_integrity(
    order_items,
    orders,
    products
):

    print("Checking referential integrity...")

    invalid_order_items = order_items[
        ~order_items["order_id"].isin(
            orders["order_id"]
        )
    ]

    invalid_product_items = order_items[
        ~order_items["product_id"].isin(
            products["product_id"]
        )
    ]

    issues.append(
        "Order items referencing non-existent orders: "
        f"{len(invalid_order_items)}"
    )

    issues.append(
        "Order items referencing non-existent products: "
        f"{len(invalid_product_items)}"
    )

    return (
        invalid_order_items,
        invalid_product_items
    )


# --------------------------------
# RUN CLEANING PIPELINE
# --------------------------------

print("\nSTARTING DATA CLEANING")

orders_clean = clean_orders(orders_df)

products_clean = clean_products(products_df)

customers_clean = clean_customers(customers_df)

order_items_clean = clean_order_items(order_items_df)


# Remove orders whose customers were removed

orders_before_customer_check = len(orders_clean)

orders_clean = orders_clean[
    orders_clean["customer_id"].isin(
        customers_clean["customer_id"]
    )
]

removed_customer_orders = (
    orders_before_customer_check
    - len(orders_clean)
)

issues.append(
    "Orders removed due to invalid customer reference: "
    f"{removed_customer_orders}"
)


# Check referential integrity

invalid_orders, invalid_products = (
    check_referential_integrity(
        order_items_clean,
        orders_clean,
        products_clean
    )
)


# Remove invalid order references

order_items_clean = order_items_clean[
    order_items_clean["order_id"].isin(
        orders_clean["order_id"]
    )
]


# Remove invalid product references

order_items_clean = order_items_clean[
    order_items_clean["product_id"].isin(
        products_clean["product_id"]
    )
]


# --------------------------------
# EXPORT CLEANED DATA
# --------------------------------

customers_clean.to_csv(
    f"{CLEAN_DATA_PATH}/customers_clean.csv",
    index=False
)

products_clean.to_csv(
    f"{CLEAN_DATA_PATH}/products_clean.csv",
    index=False
)

orders_clean.to_csv(
    f"{CLEAN_DATA_PATH}/orders_clean.csv",
    index=False
)

order_items_clean.to_csv(
    f"{CLEAN_DATA_PATH}/order_items_clean.csv",
    index=False
)


# --------------------------------
# CREATE ISSUES REPORT
# --------------------------------

with open(
    f"{OUTPUT_PATH}/issues_report.txt",
    "w"
) as file:

    file.write(
        "E-COMMERCE DATA CLEANING ISSUES REPORT\n"
    )

    file.write("=" * 45 + "\n\n")

    for issue in issues:

        file.write(issue + "\n")


# --------------------------------
# FINAL SUMMARY
# --------------------------------

print("\nDATA CLEANING COMPLETED")

print("\nCleaned Row Counts")

print(
    "Customers:",
    len(customers_clean)
)

print(
    "Products:",
    len(products_clean)
)

print(
    "Orders:",
    len(orders_clean)
)

print(
    "Order Items:",
    len(order_items_clean)
)

print(
    "\nCleaned CSV files created in data/cleaned/"
)

print(
    "Issues report created at output/issues_report.txt"
)