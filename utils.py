import json

def getConfig():
    data = None
    with open("config.json", "r") as file:
        data = json.load(file)
    return data