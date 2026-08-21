import sqlite3


DATABASE = "stock.db"


def initialize_database():
    connection = sqlite3.connect(DATABASE)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS stock (
            product_id TEXT PRIMARY KEY,
            quantity INTEGER NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()


def update_stock(items):
    connection = sqlite3.connect(DATABASE)

    for product_id, quantity in items.items():
        connection.execute(
            """
            INSERT INTO stock (product_id, quantity)
            VALUES (?, ?)
            ON CONFLICT(product_id)
            DO UPDATE SET quantity = excluded.quantity
            """,
            (product_id, quantity),
        )

    connection.commit()
    connection.close()


def get_stock():
    connection = sqlite3.connect(DATABASE)

    rows = connection.execute(
        "SELECT product_id, quantity FROM stock"
    ).fetchall()

    connection.close()

    return {product_id: quantity for product_id, quantity in rows}
