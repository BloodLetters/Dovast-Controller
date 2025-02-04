# socket.py
import asyncio
import websockets
import json

class SaweriaWebSocketListener:
    def __init__(self, stream_key, on_donation_callback, debug=False):
        self.stream_key = stream_key
        self.debug = debug
        self.on_donation_callback = on_donation_callback
        self.uri = f"wss://events.saweria.co/stream?streamKey={stream_key}"

    async def listen(self):
        while True:
            try:
                async with websockets.connect(self.uri) as websocket:
                    print("[LOG] Connected!. waiting donation")
                    while True:
                        try:
                            message = await websocket.recv()
                            data = json.loads(message)
                            
                            if self.debug:
                                print("[DEBUG] Data receive:", data)

                            if data.get("type") == "donation":
                                donation_data = data["data"][0]
                                self.on_donation_callback(donation_data)
                        except websockets.exceptions.ConnectionClosed:
                            print("[LOG] Connection closed. reconecting......")
                            break

            except Exception as e:
                print(f"[ERROR] Error: {e}. Reconnecting in 5 second")
                await asyncio.sleep(5)