import time

import requests

from stock_store import initialize_database, update_stock


WAREHOUSE_API_URL = "http://localhost:5001/warehouse/stock"
POLL_INTERVAL = 300


def poll_warehouse():
    response = requests.get(WAREHOUSE_API_URL)
    response.raise_for_status()

    stock = response.json()

    initialize_database()
    update_stock(stock)

    print(f"Updated stock store: {stock}")


if __name__ == "__main__":
    while True:
        poll_warehouse()
        print(f"Waiting {POLL_INTERVAL} seconds before the next poll...")
        time.sleep(POLL_INTERVAL)
