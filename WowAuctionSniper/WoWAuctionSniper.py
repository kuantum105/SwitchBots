import cv2
import keyboard
import numpy as np
import pyautogui
import pygetwindow
import pytesseract
import re
import time

# ---------- CONSTANTS & VARS---------- #
listings = [
    {"x": 1125, "y": 363, "coord": (1125, 363, 1335, 409)},
    {"x": 1125, "y": 427, "coord": (1125, 427, 1335, 472)},
    {"x": 1125, "y": 490, "coord": (1125, 490, 1335, 532)},
]

my_gold = {"coord": (98, 876, 150, 898)}

search_button = {"coord": (1199, 252, 1219, 267), "x": 1199, "y": 252}

binarization_thresholds = {"threshold": 127, "max": 255}

red_mask = {"lower_bound": (0, 50, 20), "upper_bound": (5, 255, 255)}
red_mask2 = {"lower_bound": (175, 50, 20), "upper_bound": (180, 255, 255)}

purchase_limit = 12.85
min_quantity = 2

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)


def get_screenshot_grey_thresholded(coords):
    ret, thresh = cv2.threshold(
        get_screenshot_grey(coords),
        binarization_thresholds["threshold"],
        binarization_thresholds["max"],
        cv2.THRESH_BINARY,
    )

    return thresh


def get_text(screenshot):
    return pytesseract.image_to_string(screenshot, config="--psm 11 -l eng")


def auction_click_search():
    pyautogui.click(search_button["x"], search_button["y"])
    return


def get_currency_from_screenshot(coords):
    screenshot = get_screenshot_grey(coords)
    text = get_text(screenshot)
    all_currency = re.findall(r"\d+", text)
    # cv2.imwrite("saved_image.jpg", screenshot)  # debugging

    if len(all_currency) == 5:
        return {
            "quantity": int(all_currency[0]),
            "currency": float(all_currency[3]) + float(all_currency[4]) / 100,
        }
    else:
        return {
            "quantity": 0,
            "currency": 999,
        }


def get_my_gold():
    screenshot = get_screenshot_grey_thresholded(my_gold["coord"])
    text = get_text(screenshot)
    cv2.imwrite("saved_image.jpg", screenshot)  # debugging

    return re.findall(r"\d+", text)


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


def check_and_purchase(position):
    stack = get_currency_from_screenshot(listings[position].get("coord"))

    if stack["currency"] < purchase_limit and stack["quantity"] >= 2:
        pyautogui.click((listings[position]["x"], listings[position]["y"]))
        keyboard.press("end")
        keyboard.release("end")
        print(
            "Attempted to Purchase "
            + str(stack["quantity"])
            + " @ "
            + str(stack["currency"])
        )

    return stack["currency"]


def welcome():
    print("############## INITIALIZED ##############")
    print("############## ARE YOU READY ##############")
    print("############## TO MAKE MONEY ##############")


# ---------- HELPERS END ---------- #

# ---------- MAIN START ---------- #

wow_client = window_get("World of Warcraft")
window_standardize(wow_client)
welcome()

while len(get_my_gold()) == 1:
    while is_search_red():
        time.sleep(0.85)
        auction_click_search()

        check_and_purchase(0)
        check_and_purchase(1)
        check_and_purchase(2)
