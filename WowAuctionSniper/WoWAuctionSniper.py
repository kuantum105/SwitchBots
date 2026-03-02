import cv2
from datetime import datetime
import keyboard
import numpy as np
import pyautogui
import pygetwindow
import easyocr
import re
import time


# ---------- CONSTANTS & VARS---------- #
listings = [
    {
        "x": 1125,
        "y": 363,
        "coord": (1125, 363, 1335, 409),
        "buyout": (1220, 389, 1333, 408),
        "quantity": (1171, 364, 1334, 382),
    },
    {
        "x": 1125,
        "y": 427,
        "coord": (1125, 427, 1335, 472),
        "buyout": (1220, 450, 1333, 474),
        "quantity": (1171, 430, 1223, 450),
    },
    {
        "x": 1125,
        "y": 490,
        "coord": (1125, 490, 1335, 532),
        "buyout": (1220, 513, 1333, 534),
        "quantity": (1171, 490, 1223, 510),
    },
]

my_gold = {"coord": (98, 876, 170, 898)}

search_button = {"coord": (1199, 252, 1219, 267), "x": 1199, "y": 252}

binarization_thresholds = {"threshold": 127, "max": 255}

red_mask = {"lower_bound": (0, 50, 20), "upper_bound": (5, 255, 255)}
red_mask2 = {"lower_bound": (175, 50, 20), "upper_bound": (180, 255, 255)}

purchase_limit = 12.85
min_quantity = 2
reader = easyocr.Reader(["en"])

window_default = {"x": 2560, "y": 1440}

debugging_verbose = True
# ---------- CONSTANTS & VARS END ---------- #

# ---------- HELPERS ---------- #


def window_get(window_title):
    return pygetwindow.getWindowsWithTitle(window_title)[0]


def window_standardize(window):
    window.resizeTo(window_default["x"], window_default["y"])
    window.moveTo(0, 0)
    window.activate()
    time.sleep(3)


def get_screenshot_colour(coords):
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.crop(coords)
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def get_screenshot_grey(coords):
    screenshot = pyautogui.screenshot()
    screenshot = screenshot.crop(coords)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(screenshot, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    return resized


def get_text(screenshot):
    return reader.readtext(screenshot, detail=0, paragraph=True)


def auction_click_search():
    pyautogui.click(search_button["x"], search_button["y"])
    return


def get_gold():
    screenshot = get_screenshot_grey(my_gold["coord"])
    text = get_text(screenshot)
    try:
        return int(text[0])
    except:
        return 0


def get_quantity(index):
    screenshot = get_screenshot_grey(listings[index].get("quantity"))
    try:
        text = get_text(screenshot)[0]

        if "x" in text.lower():
            return int(text.split("x")[0])
        else:
            return 0
    except:
        return 0


def get_buyout(index):
    screenshot = get_screenshot_grey(listings[index].get("buyout"))
    text = get_text(screenshot)
    buyout = 0
    try:
        for index, value in enumerate(text):
            value = re.sub(r"[^\d ]", "", value)
            buyout += float(value) / (100**index)
        return buyout
    except:
        return 999


def is_search_red():
    screenshot = get_screenshot_colour(search_button["coord"])
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(screenshot, red_mask["lower_bound"], red_mask["upper_bound"])
    mask2 = cv2.inRange(screenshot, red_mask2["lower_bound"], red_mask2["upper_bound"])
    mask = cv2.bitwise_or(mask1, mask2)

    if cv2.countNonZero(mask) > 0:
        return True
    else:
        return False


def check_and_purchase(index):
    buyout = get_buyout(index)
    quantity = get_quantity(index)

    if buyout < purchase_limit and quantity > 1:
        pyautogui.click((listings[index]["x"], listings[index]["y"]))
        time.sleep(0.05)
        keyboard.press("end")
        time.sleep(0.05)
        keyboard.release("end")
        print("Attempted to Purchase " + str(quantity) + " @ " + str(buyout))

    return buyout, quantity


def welcome():
    print("############## INITIALIZED ##############")
    print("############## ARE YOU READY ##############")
    print("############## TO MAKE MONEY ##############")
    print("Starting Time: " + str(datetime.now()))


# ---------- HELPERS END ---------- #

# ---------- MAIN START ---------- #

# TO STOP, CLOSE AUCTION HOUSE #
wow_client = window_get("World of Warcraft")
window_standardize(wow_client)
welcome()

while get_gold() > 1:
    while is_search_red():
        auction_click_search()
        print("------------")
        print("     Index 0: ", check_and_purchase(0))
        print("     Index 1: ", check_and_purchase(1))
        print("     Index 2: ", check_and_purchase(2))
        print("------------")

print("Ending Time: " + str(datetime.now()))
