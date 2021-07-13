import requests
from math import sqrt
import pytesseract


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


def get_items(all_items: list):

    readed_line = ""
    recognized_items = list()

    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'
    for line in pytesseract.image_to_string(r'vf3.png').split("\n"):
        if "Prime" in line:
            readed_line = line

    for item in all_items:
        if item in readed_line:
            recognized_items.append(item)

    return recognized_items


all_prime_items = [item["item_name"] for item in requests.get(
    f"https://api.warframe.market/v1/items").json()["payload"]["items"] if "_prime_" in item["url_name"]]

for item in get_items(all_prime_items):
    print(item, possible_sell_price(item))
