import sqlite3
import os


DATABASE_PATH = "database/ecommerce.db"

SQL_FILES = [
    "sql/aggregations.sql",
    "sql/window_functions.sql",
    "sql/cohort_analysis.sql"
]


def run_sql_file(file_path):

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    cursor = connection.cursor()

    with open(file_path, "r") as file:
        sql_content = file.read()

    queries = sql_content.split(";")

    print("\n" + "=" * 70)

    print(
        "RUNNING SQL FILE:",
        file_path
    )

    print("=" * 70)

    query_number = 1

    for query in queries:

        query = query.strip()

        if not query:
            continue

        try:

            cursor.execute(query)

            rows = cursor.fetchall()

            column_names = [
                description[0]
                for description
                in cursor.description
            ]

            print(
                f"\nQUERY {query_number}"
            )

            print("-" * 70)

            print(
                " | ".join(column_names)
            )

            print("-" * 70)

            if not rows:

                print(
                    "No records found"
                )

            else:

                for row in rows[:20]:

                    print(
                        " | ".join(
                            str(value)
                            for value in row
                        )
                    )

                if len(rows) > 20:

                    print(
                        f"... {len(rows) - 20} more rows"
                    )

            query_number += 1

        except sqlite3.Error as error:

            print(
                "\nSQL ERROR:",
                error
            )

            print(
                "QUERY:"
            )

            print(query)

            connection.close()

            return

    connection.close()


for sql_file in SQL_FILES:

    if os.path.exists(sql_file):

        run_sql_file(sql_file)

    else:

        print(
            "SQL file not found:",
            sql_file
        )