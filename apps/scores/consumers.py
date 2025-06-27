import json
from channels.generic.websocket import AsyncWebsocketConsumer

class BadmintonConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f'badminton_{self.match_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(self.group_name, {
            'type': 'score_update',
            'scoreA': data['scoreA'],
            'scoreB': data['scoreB'],
            'totalPoints': data['totalPoints'],
            'commentary': data['commentary'],
        })

    async def score_update(self, event):
        await self.send(text_data=json.dumps(event))