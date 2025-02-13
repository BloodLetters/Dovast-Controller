import asyncio
import websockets
import json
import re

from loguru import logger

class StreamlabsClient:
    def __init__(self, socketToken, callback=None):
        self.callback = callback
        self.token = socketToken
        self.socket_url = f'wss://sockets.streamlabs.com/socket.io/?token={self.token}&EIO=3&transport=websocket'

    async def listen(self):
        while True:
            try:
                async with websockets.connect(self.socket_url) as ws:
                    logger.success('Connected to Streamlabs WebSocket')
                    while True:
                        message = await ws.recv()
                        try:
                            match = re.match(r'42\["event",(.*)\]', message)
                            if match:
                                parsed_data = json.loads(match.group(1))
                                if parsed_data.get('type') == 'donation':
                                    donations = parsed_data.get('message', [])
                                    for donation in donations:
                                        donation_info = {
                                            "name": donation.get('from', 'Unknown'),
                                            "amount": int(str(donation.get('amount', '0')).replace(".", "").replace("Rp ", ""))
                                        }
                                        if self.callback:
                                            self.callback(donation_info)
                        except (json.JSONDecodeError, ValueError, KeyError) as e:
                            logger.error('Error parsing message:', e)
            except (websockets.exceptions.ConnectionClosed, asyncio.TimeoutError, websockets.exceptions.InvalidMessage) as e:
                logger.warning(f'Connection lost: {e}, reconnecting...')
                await asyncio.sleep(5)

    def connect(self):
        asyncio.run(self.listen())
