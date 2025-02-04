import os
import json
import asyncio
import re

from pynput.keyboard import Controller
from pynput.mouse import Controller as MouseController, Button
from connection.saweria import SaweriaClient
from connection.trakteer import TrakteerClient
from utils import getConfig
from loguru import logger

logger.add("logs/app.log", 
           format="{time} | {level} | {module}:{function}:{line} - {message}", 
           rotation="1 MB")
keyboard = Controller()
mouse = MouseController()
config = getConfig()

def load_keys():
    keys = []
    keys_folder = "keys" 
    try:
        for filename in os.listdir(keys_folder):
            if filename.endswith(".json"):
                with open(os.path.join(keys_folder, filename), "r") as file:
                    data = json.load(file)
                    keys.append(data)
        return keys
    except FileNotFoundError:
        # print("Folder keys Not Found!")
        logger.error("Folder 'Keys' Not found!")
        exit()

async def slide_mouse(direction, amount, step=5, delay=0.01):
    steps = abs(amount) // step
    remainder = abs(amount) % step

    dx, dy = 0, 0
    if direction == "right":
        dx, dy = step, 0
    elif direction == "left":
        dx, dy = -step, 0
    elif direction == "up":
        dx, dy = 0, -step
    elif direction == "down":
        dx, dy = 0, step

    logger.log(f"[DONATION] Sliding mouse {direction} by {amount} pixels")

    for _ in range(steps):
        mouse.move(dx, dy)
        await asyncio.sleep(delay) 

    if remainder:
        mouse.move(dx // abs(dx) * remainder if dx else 0, 
                   dy // abs(dy) * remainder if dy else 0)

async def trigger_key(type, key):
    key = key.lower()
    type = type.lower()

    if type.lower() == "mouse":
        if key in ["left_click", "middle_click", "right_click"]:
            logger.log(f"[DONATION] Clicking mouse: {key}")
            if key == "left_click":
                mouse.click(Button.left)
            elif key == "middle_click":
                mouse.click(Button.middle)
            elif key == "right_click":
                mouse.click(Button.right)
            else:
                logger.warning("[DONATION] mouse event triggered but did not doin any action. are you setup it correctly?")
        else:
            match = re.match(r"slide_(right|left|up|down)\((\d+)\)", key)
            if match:
                direction, amount = match.groups()
                amount = int(amount)
                await slide_mouse(direction, amount)
            else:
                logger.warning("[DONATION] mouse event triggered but did not doin any action. are you setup it correctly?")

    elif type.lower() == "key":
        logger.info(f"[DONATION] Pressing key: {key}")
        keyboard.press(key)
        keyboard.release(key)

    else:
        logger.warning("[DONATION] Donation found but did not trigger any action. are you setup it correctly?")

def on_donation(donation_data):
    amount = donation_data.get("amount")
    logger.success(f"Donation received! Amount: {amount}")
    isPriceFound = False

    for key_binding in keys:
        if key_binding["price"] == amount:
            isPriceFound = True
            logger.success(f"Keybinds {key_binding} found with amount {amount}")
            asyncio.create_task(trigger_key(key_binding['type'], key_binding["key"]))
    
    if isPriceFound == False:
       logger.warning(f"Donation found but no price matched. have you set it up correctly?") 

if __name__ == "__main__":
    keys = load_keys()
    logger.info(f"Loaded keybinds: {keys}")
    if(config['service'].lower() == "saweria"):
        saweria_key = config['saweria']['stream_key']
        if(saweria_key == ""): 
            logger.error("stream_key is none")
            exit()
        listener = SaweriaClient(saweria_key, on_donation, config['debug'])
        asyncio.run(listener.listen())
    elif(config['service'].lower() == "trakteer"):
        trakteer_data = config['trakteer']
        if(trakteer_data['channel'] == "" or trakteer_data['test_channel'] == ""):
            logger.error("channel or test_channel is none")
            exit()
        else:
            client = TrakteerClient(trakteer_data['channel'], trakteer_data['test_channel'], callback=on_donation)
            asyncio.run(client.connect())
    else:
        logger.error("Service not found!")
        exit()