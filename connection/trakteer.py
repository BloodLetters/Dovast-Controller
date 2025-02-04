import asyncio
import websockets
import json

from utils import getConfig
from loguru import logger


class TrakteerClient:
    def __init__(self, channel_name, test_channel_name, callback=None):
        self.ws_url = f"wss://socket.trakteer.id/app/2ae25d102cc6cd41100a?protocol=7&client=js&version=5.1.1&flash=false"
        self.channel_name = channel_name
        self.test_channel_name = test_channel_name
        self.socket_id = None
        self.on_donation_callback = callback 
        self.debug = getConfig()['debug']

    async def connect(self):
        while True:
            try:
                async with websockets.connect(self.ws_url) as websocket:
                    logger.info("Connected to trakteer websocket. Waiting donation!")
                    message = await websocket.recv()
                    data = json.loads(message)
                    if(self.debug):
                        logger.debug("[DEBUG] Data receive:", data)

                    if data['event'] == 'pusher:connection_established':
                        self.socket_id = json.loads(data['data'])['socket_id']
                        await self.subscribe(websocket)

                        await self.listen_donations(websocket)
            
            except (websockets.ConnectionClosed, asyncio.TimeoutError) as e:
                logger.warning(f"error: {e}. Reconnectingg in 5 second...")
                await asyncio.sleep(5) 

    async def subscribe(self, websocket):
        for channel in [self.channel_name, self.test_channel_name]:
            subscribe_message = {
                "event": "pusher:subscribe",
                "data": {
                    "channel": channel
                }
            }
            await websocket.send(json.dumps(subscribe_message))
            if(self.debug):
                logger.info(f"Success to logging {channel}...")

    async def listen_donations(self, websocket):
        try:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                
                if(self.debug):
                    logger.debug("[DEBUG] Donation data receive:", data)

                if data.get('event') == 'Illuminate\\Notifications\\Events\\BroadcastNotificationCreated':
                    donation_data = json.loads(data['data'])
                    donation_info = {
                        "name": donation_data['supporter_name'],
                        "amount": int(donation_data['price'].replace(".", "").replace("Rp ", "")) * int(donation_data['quantity'])
                    }

                    logger.success(f"Donation found: {donation_info['name']} - {donation_info['amount']}")

                    if self.on_donation_callback:
                        self.on_donation_callback(donation_info)

        except websockets.ConnectionClosed:
            logger.error("Connection closed!")
            raise 