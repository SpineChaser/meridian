import requests

from stock_cache import update_stock


WAREHOUSE_API_URL = "http://localhost:5001/warehouse/stock"


def poll_warehouse():
    response = requests.get(WAREHOUSE_API_URL)
    response.raise_for_status()

    stock = response.json()
    update_stock(stock)

    print(f"Updated stock cache: {stock}")


if __name__ == "__main__":
    poll_warehouse()
