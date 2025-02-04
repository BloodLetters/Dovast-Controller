import os
import json
import asyncio
import re

from pynput.keyboard import Controller
from pynput.mouse import Controller as MouseController, Button
from connection.saweria import SaweriaWebSocketListener
from utils import getConfig

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
        print("[ERROR] Folder keys Not Found!")
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

    print(f"[DONATION] Sliding mouse {direction} by {amount} pixels")

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
            print(f"[DONATION] Clicking mouse: {key}")
            if key == "left_click":
                mouse.click(Button.left)
            elif key == "middle_click":
                mouse.click(Button.middle)
            elif key == "right_click":
                mouse.click(Button.right)
            else:
                print("[DONATION] mouse event triggered but did not doin any action")
                print("[DONATION] are you setup it correctly?")
        else:
            match = re.match(r"slide_(right|left|up|down)\((\d+)\)", key)
            if match:
                direction, amount = match.groups()
                amount = int(amount)
                await slide_mouse(direction, amount)
            else:
                print("[DONATION] mouse event triggered but did not doin any action")
                print("[DONATION] are you setup it correctly?")

    elif type.lower() == "key":
        print(f"[DONATION] Pressing key: {key}")
        keyboard.press(key)
        keyboard.release(key)

    else:
        print("[DONATION] Donation found but did not trigger any action")
        print("[DONATION] are you setup it correctly?")

def on_donation(donation_data):
    amount = donation_data.get("amount")
    print(f"[LOG] Donation received! Amount: {amount}")

    for key_binding in keys:
        if key_binding["price"] == amount:
            print(f"[LOG] Keybinds {key_binding} found with amount {amount}")
            asyncio.create_task(trigger_key(key_binding['type'], key_binding["key"]))

keys = load_keys()
print("[LOG] Loaded keybinds:", keys)
if(config['service'] == "saweria"):
    saweria_key = config['saweria']['stream_key']
    if(saweria_key == ""): 
        print("[ERROR] stream_key is none")
        exit()
    listener = SaweriaWebSocketListener(saweria_key, on_donation, config['debug'])
    asyncio.run(listener.listen())
else:
    print("[ERROR] Service not found!")
    exit()