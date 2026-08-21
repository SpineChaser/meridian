stock_cache = {}


def update_stock(items):
    global stock_cache
    stock_cache = items


def get_stock():
    return stock_cache
