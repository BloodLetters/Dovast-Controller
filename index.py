import os
import json
import asyncio

from pynput.keyboard import Controller
from server import SaweriaWebSocketListener
from utils import getConfig

keyboard = Controller()

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

def trigger_key(key):
    print(f"Menekan tombol: {key}")
    keyboard.press(key)
    keyboard.release(key)

def on_donation(donation_data):
    amount = donation_data.get("amount")
    print(f"[LOG] Donation received! Amount: {amount}")

    for key_binding in keys:
        if key_binding["price"] == amount:
            print(f"[LOG] Keybinds {key_binding} found with amount {amount}")
            trigger_key(key_binding["key"])

keys = load_keys()
config = getConfig()
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