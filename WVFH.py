import requests
from math import sqrt


def possible_sell_price(name: str):

    name = name.lower().replace(" ", "_")
    prices = list()
    amount = 10

    orders = requests.get(
        f"https://api.warframe.market/v1/items/{name}/orders").json()["payload"]["orders"]

    for order in orders:
        if order["platform"] == "pc" and order["region"] == "en" and order["order_type"] == "sell" and order["user"]["status"] == "ingame":
            prices.append(order["platinum"])

    prices.sort()
    prices = prices[:amount]
    amount = len(prices)

    mean = sum(prices)/len(prices)
    std = sqrt(
        sum([(mean - price)**2 for price in prices]) / (amount-1))

    return round(mean - std/2, 1)
