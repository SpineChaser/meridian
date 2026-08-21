import requests

from stock_store import initialize_database, update_stock


WAREHOUSE_API_URL = "http://localhost:5001/warehouse/stock"


def poll_warehouse():
    response = requests.get(WAREHOUSE_API_URL)
    response.raise_for_status()

    stock = response.json()

    initialize_database()
    update_stock(stock)

    print(f"Updated stock store: {stock}")


if __name__ == "__main__":
    poll_warehouse()
