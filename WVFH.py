from os import error
from tkinter.constants import S
import requests
from math import sqrt
import pytesseract
import cv2
import pyautogui
import numpy as np
import tkinter as tk
from tkinter.filedialog import askopenfilename
import keyboard


# TODO: wyszukiwać po słowie np "destereza" pomijając prime i np. handle i podawać ceny całych setów

def possible_sell_price(name: str):

    # set_name = name.split()
    # set_name[-1] = "Set"
    # set_name = " ".join(set_name)
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


def get_items(all_items: list, reg: dict):

    readed_line = ""
    recognized_items = list()

    img = pyautogui.screenshot(
        region=(reg["left"], reg["top"], reg["right"] - reg["left"], reg["bottom"] - reg["top"]))
    img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    # cv2.imshow("Screenshot", img)
    # cv2.waitKey(0)

    for line in pytesseract.image_to_string(img).split("\n"):
        if "Prime" in line:
            readed_line = line

    for item in all_items:
        if item in readed_line:
            recognized_items.append(item)

    return recognized_items


def read_settings(can_open_new_setup: bool = True):
    try:
        with open("config.txt", "r") as file:
            reg = dict()
            tesseract_location = file.readline().rstrip()
            reg["left"] = int(file.readline().rstrip())
            reg["top"] = int(file.readline().rstrip())
            reg["right"] = int(file.readline().rstrip())
            reg["bottom"] = int(file.readline().rstrip())

        if tesseract_location == "error" or tesseract_location == "":
            raise ValueError

        return tesseract_location, reg

    except (FileNotFoundError, ValueError):
        if can_open_new_setup:
            setup = Setup(master=tk.Tk())
            setup.mainloop()
        else:
            return tesseract_location, reg


class Setup(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.winfo_toplevel().title("Warframe void fissure helper Setup")
        self.pack()

        self.new_location = str()
        self.new_reg = dict()

        self.create_widgets()

    def create_widgets(self):
        self.location_label = tk.Label(self)
        self.location_label["text"] = "Select Tesseract exe file\nDefault: C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        self.location_label.pack(side="top")

        self.locate_tesseract = tk.Button(self)
        self.locate_tesseract["text"] = "Select Tesseract file"
        self.locate_tesseract["command"] = self.save_tesseract_location
        self.locate_tesseract.pack(side="top")

        self.setup_corners_label = tk.Label(self)
        self.setup_corners_label["text"] = "Click button bellow, then hover mouse over the corner and click SPACE"
        self.setup_corners_label.pack(side="top")

        self.setup_first_corner = tk.Button(self)
        self.setup_first_corner["text"] = "Setup first corner"
        self.setup_first_corner["command"] = self.save_first_corner
        self.setup_first_corner.pack(side="top")

        self.setup_second_corner = tk.Button(self)
        self.setup_second_corner["text"] = "Setup second corner"
        self.setup_second_corner["command"] = self.save_second_corner
        self.setup_second_corner.pack(side="top")

        self.save_changes_button = tk.Button(self)
        self.save_changes_button["text"] = "Save changes"
        self.save_changes_button["command"] = self.save_changes
        self.save_changes_button.pack(side="top")

        self.quit = tk.Button(self, text="Quit", command=self.master.destroy)
        self.quit.pack(side="bottom")

    def save_tesseract_location(self):
        self.new_location = askopenfilename()

    def save_first_corner(self):
        while True:
            try:
                if keyboard.is_pressed('space'):
                    pos = pyautogui.position()
                    self.new_reg["left"] = pos.x
                    self.new_reg["top"] = pos.y
                    break
            except:
                break

    def save_second_corner(self):
        while True:
            try:
                if keyboard.is_pressed('space'):
                    pos = pyautogui.position()
                    self.new_reg["right"] = pos.x
                    self.new_reg["bottom"] = pos.y
                    break
            except:
                break

    def save_changes(self):

        actual_location = None
        actual_reg = None

        try:
            with open("config.txt", "r") as file:
                pass
            actual_location, actual_reg = read_settings(
                can_open_new_setup=False)
        except FileNotFoundError:
            pass

        with open("config.txt", "w") as file:
            if self.new_location != str():
                file.write(self.new_location+"\n")
            elif actual_location != None:
                file.write(actual_location+"\n")
            else:
                file.write("error\n")

            if len(self.new_reg) == 4:
                file.writelines([str(self.new_reg["left"])+"\n", str(self.new_reg["top"])+"\n",
                                 str(self.new_reg["right"])+"\n", str(self.new_reg["bottom"])])

            elif actual_reg != None:
                file.writelines([str(actual_reg["left"])+"\n", str(actual_reg["top"])+"\n",
                                 str(actual_reg["right"])+"\n", str(actual_reg["bottom"])])


class App(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.winfo_toplevel().title("Warframe void fissure helper")
        self.pack()

        self.all_prime_items = [item["item_name"] for item in requests.get(
            f"https://api.warframe.market/v1/items").json()["payload"]["items"] if "_prime_" in item["url_name"]]

        self.create_widgets()

    def create_widgets(self):

        self.listen_label = tk.Label(self)
        self.listen_label["text"] = "Click 'Listen' button, and when you can see your opened fissures press '\\'"
        self.listen_label.pack(side="top")

        self.listen_button = tk.Button(
            self, text="Listen", command=self.listen)
        self.listen_button.pack(side="top")

        self.items_display = tk.Label(self)
        self.items_display["text"] = ""
        self.items_display.pack(side="top")

        self.setup = tk.Button(self, text="Setup", command=self.launch_setup)
        self.setup.pack(side="top")

        self.quit = tk.Button(self, text="Quit", command=self.master.destroy)
        self.quit.pack(side="bottom")

    def listen(self):
        while True:
            try:
                if keyboard.is_pressed('\\'):
                    self.find_prices()
                    break
            except:
                break

    def launch_setup(self):
        setup = Setup(master=tk.Tk())
        setup.mainloop()

    def find_prices(self):
        location, reg = read_settings()
        pytesseract.pytesseract.tesseract_cmd = location

        found_items = str()

        for item in get_items(self.all_prime_items, reg):
            found_items += (item + " - " +
                            str(possible_sell_price(item))) + "\n"

        self.items_display["text"] = found_items
        self.items_display.pack()


app = App(master=tk.Tk())
app.mainloop()
