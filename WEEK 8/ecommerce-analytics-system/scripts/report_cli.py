import sqlite3
import argparse
import sys


DATABASE_PATH = "database/ecommerce.db"


REPORT_QUERIES = {

    "revenue": """
        SELECT
            p.category,
            ROUND(
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (1 - oi.discount_percent / 100.0)
                ),
                2
            ) AS total_revenue

        FROM order_items oi

        JOIN products p
            ON oi.product_id = p.product_id

        JOIN orders o
            ON oi.order_id = o.order_id

        WHERE o.status != 'CANCELLED'

        GROUP BY p.category

        ORDER BY total_revenue DESC
    """,


    "top_customers": """
        SELECT
            c.customer_id,
            c.customer_name,

            ROUND(
                SUM(
                    oi.quantity
                    * oi.unit_price
                    * (1 - oi.discount_percent / 100.0)
                ),
                2
            ) AS lifetime_value

        FROM customers c

        JOIN orders o
            ON c.customer_id = o.customer_id

        JOIN order_items oi
            ON o.order_id = oi.order_id

        WHERE o.status != 'CANCELLED'

        GROUP BY
            c.customer_id,
            c.customer_name

        ORDER BY lifetime_value DESC

        LIMIT 10
    """,


    "monthly": """
        SELECT
            strftime(
                '%Y-%m',
                order_date
            ) AS order_month,

            COUNT(order_id) AS total_orders

        FROM orders

        GROUP BY order_month

        ORDER BY order_month
    """,


    "retention": """
        WITH customer_first_purchase AS (
            SELECT
                customer_id,
                MIN(order_date) AS first_purchase_date

            FROM orders

            GROUP BY customer_id
        ),

        customer_activity AS (
            SELECT DISTINCT
                o.customer_id,

                strftime(
                    '%Y-%m',
                    cfp.first_purchase_date
                ) AS cohort_month,

                (
                    (
                        CAST(
                            strftime('%Y', o.order_date)
                            AS INTEGER
                        )
                        -
                        CAST(
                            strftime(
                                '%Y',
                                cfp.first_purchase_date
                            )
                            AS INTEGER
                        )
                    ) * 12

                    +

                    (
                        CAST(
                            strftime('%m', o.order_date)
                            AS INTEGER
                        )
                        -
                        CAST(
                            strftime(
                                '%m',
                                cfp.first_purchase_date
                            )
                            AS INTEGER
                        )
                    )
                ) AS month_number

            FROM orders o

            JOIN customer_first_purchase cfp
                ON o.customer_id = cfp.customer_id
        ),

        cohort_size AS (
            SELECT
                cohort_month,

                COUNT(
                    DISTINCT customer_id
                ) AS total_customers

            FROM customer_activity

            WHERE month_number = 0

            GROUP BY cohort_month
        ),

        retention AS (
            SELECT
                cohort_month,
                month_number,

                COUNT(
                    DISTINCT customer_id
                ) AS retained_customers

            FROM customer_activity

            GROUP BY
                cohort_month,
                month_number
        )

        SELECT
            r.cohort_month,
            r.month_number,
            r.retained_customers,
            cs.total_customers,

            ROUND(
                r.retained_customers
                * 100.0
                / NULLIF(
                    cs.total_customers,
                    0
                ),
                2
            ) AS retention_rate_percent

        FROM retention r

        JOIN cohort_size cs
            ON r.cohort_month = cs.cohort_month

        ORDER BY
            r.cohort_month,
            r.month_number

        LIMIT 30
    """,


    "segments": """
        WITH customer_frequency AS (
            SELECT
                c.customer_id,
                c.customer_name,

                COUNT(
                    DISTINCT o.order_id
                ) AS total_orders

            FROM customers c

            LEFT JOIN orders o
                ON c.customer_id = o.customer_id

            GROUP BY
                c.customer_id,
                c.customer_name
        )

        SELECT
            customer_id,
            customer_name,
            total_orders,

            CASE
                WHEN total_orders <= 1
                    THEN 'ONE-TIME'

                WHEN total_orders BETWEEN 2 AND 4
                    THEN 'OCCASIONAL'

                ELSE 'LOYAL'
            END AS frequency_segment

        FROM customer_frequency

        ORDER BY total_orders DESC

        LIMIT 20
    """,


    "returns": """
        SELECT
            p.category,

            SUM(
                CASE
                    WHEN oi.quantity < 0
                    THEN ABS(oi.quantity)
                    ELSE 0
                END
            ) AS returned_items,

            SUM(
                ABS(oi.quantity)
            ) AS total_items,

            ROUND(
                100.0
                * SUM(
                    CASE
                        WHEN oi.quantity < 0
                        THEN ABS(oi.quantity)
                        ELSE 0
                    END
                )
                / NULLIF(
                    SUM(ABS(oi.quantity)),
                    0
                ),
                2
            ) AS return_rate_percent

        FROM order_items oi

        JOIN products p
            ON oi.product_id = p.product_id

        GROUP BY p.category

        ORDER BY return_rate_percent DESC
    """
}


def connect_database():

    try:

        connection = sqlite3.connect(
            DATABASE_PATH
        )

        return connection

    except sqlite3.Error as error:

        print(
            "Database connection error:",
            error
        )

        sys.exit(1)


def print_table(columns, rows):

    if not rows:

        print("\nNo records found.")
        return

    widths = []

    for index, column in enumerate(columns):

        max_width = len(str(column))

        for row in rows:

            value_width = len(
                str(row[index])
            )

            if value_width > max_width:
                max_width = value_width

        widths.append(max_width)


    separator = "+"

    for width in widths:

        separator += (
            "-" * (width + 2)
            + "+"
        )


    print(separator)

    header = "|"

    for index, column in enumerate(columns):

        header += (
            " "
            + str(column).ljust(widths[index])
            + " |"
        )

    print(header)

    print(separator)


    for row in rows:

        row_text = "|"

        for index, value in enumerate(row):

            row_text += (
                " "
                + str(value).ljust(widths[index])
                + " |"
            )

        print(row_text)


    print(separator)


def run_report(report_name):

    if report_name not in REPORT_QUERIES:

        print(
            "\nInvalid report name:",
            report_name
        )

        print(
            "\nAvailable reports:"
        )

        for report in REPORT_QUERIES:

            print(
                "-",
                report
            )

        return


    connection = connect_database()

    cursor = connection.cursor()


    try:

        cursor.execute(
            REPORT_QUERIES[report_name]
        )

        rows = cursor.fetchall()

        columns = [
            description[0]
            for description
            in cursor.description
        ]


        print(
            "\nE-COMMERCE ANALYTICS REPORT"
        )

        print(
            "Report:",
            report_name.upper()
        )

        print()


        print_table(
            columns,
            rows
        )


    except sqlite3.Error as error:

        print(
            "SQL execution error:",
            error
        )


    finally:

        connection.close()


def main():

    parser = argparse.ArgumentParser(
        description=(
            "E-Commerce Analytics "
            "Command Line Reporting Tool"
        )
    )


    parser.add_argument(
        "--report",
        required=True,
        help=(
            "Report name: revenue, "
            "top_customers, monthly, "
            "retention, segments, returns"
        )
    )


    args = parser.parse_args()


    run_report(
        args.report
    )


if __name__ == "__main__":

    main()