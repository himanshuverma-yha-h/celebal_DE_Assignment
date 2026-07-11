import sqlite3
import tempfile
import os
from datetime import datetime, timedelta


def create_test_database():
    temp_file = tempfile.NamedTemporaryFile(
        suffix=".db",
        delete=False
    )

    database_path = temp_file.name
    temp_file.close()

    connection = sqlite3.connect(database_path)

    connection.execute("PRAGMA foreign_keys = ON")

    cursor = connection.cursor()

    cursor.executescript("""
        CREATE TABLE customers (
            customer_id INTEGER PRIMARY KEY,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL
        );

        CREATE TABLE products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT NOT NULL,
            cost_price REAL NOT NULL
        );

        CREATE TABLE orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,

            FOREIGN KEY (customer_id)
                REFERENCES customers(customer_id)
        );

        CREATE TABLE order_items (
            item_id INTEGER PRIMARY KEY,
            order_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            discount_percent REAL NOT NULL,

            FOREIGN KEY (order_id)
                REFERENCES orders(order_id),

            FOREIGN KEY (product_id)
                REFERENCES products(product_id)
        );
    """)

    return connection, database_path


def close_test_database(connection, database_path):

    connection.close()

    if os.path.exists(database_path):
        os.remove(database_path)


# --------------------------------
# TEST 1
# ZERO ORDERS
# --------------------------------

def test_zero_orders():

    connection, database_path = create_test_database()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO customers
        VALUES (
            1,
            'Test Customer',
            'test@example.com'
        )
    """)

    cursor.execute("""
        SELECT COUNT(*)
        FROM orders
    """)

    order_count = cursor.fetchone()[0]

    assert order_count == 0

    print(
        "PASS - Zero orders handled correctly"
    )

    close_test_database(
        connection,
        database_path
    )


# --------------------------------
# TEST 2
# SINGLE CUSTOMER
# --------------------------------

def test_single_customer():

    connection, database_path = create_test_database()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO customers
        VALUES (
            1,
            'Single Customer',
            'single@example.com'
        )
    """)

    cursor.execute("""
        SELECT COUNT(*)
        FROM customers
    """)

    customer_count = cursor.fetchone()[0]

    assert customer_count == 1

    print(
        "PASS - Single customer handled correctly"
    )

    close_test_database(
        connection,
        database_path
    )


# --------------------------------
# TEST 3
# FUTURE DATE
# --------------------------------

def test_future_date():

    connection, database_path = create_test_database()

    cursor = connection.cursor()

    future_date = (
        datetime.now()
        + timedelta(days=365)
    ).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO customers
        VALUES (
            1,
            'Future Customer',
            'future@example.com'
        )
    """)

    cursor.execute(
        """
        INSERT INTO orders
        VALUES (
            1,
            1,
            ?,
            'PLACED'
        )
        """,
        (future_date,)
    )

    cursor.execute("""
        SELECT COUNT(*)
        FROM orders
        WHERE date(order_date) > date('now')
    """)

    future_order_count = cursor.fetchone()[0]

    assert future_order_count == 1

    print(
        "PASS - Future date detected correctly"
    )

    close_test_database(
        connection,
        database_path
    )


# --------------------------------
# TEST 4
# FOREIGN KEY ERROR
# --------------------------------

def test_invalid_foreign_key():

    connection, database_path = create_test_database()

    cursor = connection.cursor()

    foreign_key_error_detected = False

    try:

        cursor.execute("""
            INSERT INTO orders
            VALUES (
                1,
                999,
                '2026-01-01 10:00:00',
                'PLACED'
            )
        """)

    except sqlite3.IntegrityError:

        foreign_key_error_detected = True

    assert foreign_key_error_detected is True

    print(
        "PASS - Invalid foreign key rejected"
    )

    close_test_database(
        connection,
        database_path
    )


# --------------------------------
# TEST 5
# EMPTY RESULT SET
# --------------------------------

def test_empty_result_set():

    connection, database_path = create_test_database()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM orders
        WHERE status = 'DELIVERED'
    """)

    rows = cursor.fetchall()

    assert len(rows) == 0

    print(
        "PASS - Empty result set handled correctly"
    )

    close_test_database(
        connection,
        database_path
    )


# --------------------------------
# RUN TESTS
# --------------------------------

def run_tests():

    print(
        "\nRUNNING EDGE CASE TESTS\n"
    )

    test_zero_orders()

    test_single_customer()

    test_future_date()

    test_invalid_foreign_key()

    test_empty_result_set()

    print(
        "\nALL EDGE CASE TESTS PASSED"
    )


if __name__ == "__main__":

    run_tests()