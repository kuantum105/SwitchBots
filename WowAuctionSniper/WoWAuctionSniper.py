import cv2
from datetime import datetime, timedelta
import keyboard
import numpy as np
import pyautogui
import pygetwindow
import easyocr
import re
import time


# ---------- CONSTANTS & VARS---------- #

purchase_limit = 12.85
min_quantity = 2

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

sell_button = {"x": 826, "y": 933}

browse_button = {"x": 85, "y": 936}

sell_silver = {"x": 640, "y": 310}

sell_copper = {"x": 725, "y": 307}

sell_quantity = {"x": 493, "y": 412}

sell_stack = {"x": 743, "y": 414}

post_btn_coord = (910, 405, 930, 418)

buy_btn_coord = (1013, 879, 1049, 901)

# sell_window_coord = (32, 476, 432, 866)

img_netherweave_cloth = cv2.imread("reference_images/netherweave_cloth.jpg")

my_gold = {"coord": (98, 876, 170, 898)}

search_button = {"coord": (1199, 252, 1219, 267), "x": 1199, "y": 252}


binarization_thresholds = {"threshold": 127, "max": 255}

red_mask = {"lower_bound": (0, 50, 20), "upper_bound": (5, 255, 255)}
red_mask2 = {"lower_bound": (175, 50, 20), "upper_bound": (180, 255, 255)}

reader = easyocr.Reader(["en"])

window_default = {"x": 2560, "y": 1440}

debugging_verbose = True
# ---------- CONSTANTS & VARS END ---------- #


# ---------- HELPERS ---------- #
class EventTimeoutError(Exception):
    def __init__(self, message="Event Timed Out"):
        super().__init__(message)


class ImageNotFound(Exception):
    def __init__(self, message="Image Not Found"):
        super().__init__(message)


def wait_for_event(event_func, timeout=30, period=0.25):
    end_time = time.time() + timeout
    while time.time() < end_time:
        if event_func():
            return True
        time.sleep(period)
    raise EventTimeoutError()


def window_get(window_title):
    return pygetwindow.getWindowsWithTitle(window_title)[0]


def window_standardize(window):
    window.resizeTo(window_default["x"], window_default["y"])
    window.moveTo(0, 0)
    window.activate()
    time.sleep(1.25)


def get_screenshot_colour(coords, crop=True):
    screenshot = pyautogui.screenshot()
    if crop:
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
    click_and_wait(search_button["x"], search_button["y"])
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
            return 1
    except:
        return 1


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


def is_red(coord):
    screenshot = get_screenshot_colour(coord)
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

    if buyout < purchase_limit and quantity >= min_quantity:
        click_and_wait(listings[index]["x"], listings[index]["y"])
        time.sleep(0.085)
        keyboard.press("end")
        keyboard.release("end")
        print("Attempted to Purchase " + str(quantity) + " @ " + str(buyout))

    return buyout, quantity


def anti_afk():
    key_press_release("a")
    key_press_release("d")

    return datetime.now()


def click_and_wait(x, y, wait=0.125, duration=0.01):
    pyautogui.moveTo(x, y, duration)
    pyautogui.click(x, y)
    time.sleep(wait)
    return


def find_image_loc_in_image(target, image, threshold=0.95):
    results = cv2.matchTemplate(np.array(image), target, cv2.TM_SQDIFF_NORMED)
    min_confidence, _, minimum_location, _ = cv2.minMaxLoc(results)

    confidence = 1 - min_confidence

    if confidence >= threshold:
        return minimum_location
    else:
        raise ImageNotFound()


def click_netherweave():
    x, y = find_image_loc_in_image(
        img_netherweave_cloth, get_screenshot_colour(None, crop=False)
    )
    click_and_wait(x, y, wait=0.5)
    return x, y


def key_press_release(keys):
    if isinstance(keys, str):
        keys = [keys]

    for key in keys:
        keyboard.press(key)
        time.sleep(0.0625)
        keyboard.release(key)


def list_item(click_item_func, min_price, quantity="1", stack="1"):
    try:
        click_item_func()
        wait_for_event(lambda: is_red(buy_btn_coord))
        click_and_wait(
            sell_silver["x"],
            sell_silver["y"],
        )

        for char in min_price["silver"]:
            key_press_release(char)

        click_and_wait(
            sell_copper["x"],
            sell_copper["y"],
        )

        for char in min_price["copper"]:
            key_press_release(char)

        click_and_wait(
            sell_quantity["x"],
            sell_quantity["y"],
        )

        for char in quantity:
            key_press_release(char)

        click_and_wait(
            sell_stack["x"],
            sell_stack["y"],
        )

        for char in stack:
            key_press_release(char)

        wait_for_event(lambda: is_red(post_btn_coord))

        click_and_wait(post_btn_coord[0], post_btn_coord[1])
    except EventTimeoutError:
        print("Failed to List Item, Timeout Exceeded")

    return


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
afk_timer = datetime.now()
undercut_timer = datetime.now()
gold_start = get_gold()
welcome()

while get_gold() > 1:
    while is_red(search_button["coord"]):
        auction_click_search()
        time.sleep(0.125)

        if afk_timer <= (datetime.now() - timedelta(minutes=4)):
            print("Activating Anti AFK")
            afk_timer = anti_afk()

        print("------------")
        print("     Index 0: ", check_and_purchase(0))
        print("     Index 1: ", check_and_purchase(1))
        print("     Index 2: ", check_and_purchase(2))
        print("------------")

        if undercut_timer <= (datetime.now() - timedelta(minutes=3, seconds=0)):
            click_and_wait(sell_button["x"], sell_button["y"])
            list_item(click_netherweave, {"silver": "10", "copper": "38"})
            click_and_wait(browse_button["x"], browse_button["y"])
            undercut_timer = datetime.now()

print("Ending Time: " + str(datetime.now()))
print("Starting Gold: " + str(gold_start))
