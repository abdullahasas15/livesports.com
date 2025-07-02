from channels.generic.websocket import AsyncWebsocketConsumer
import json
from apps.tournaments.models import Match
from asgiref.sync import sync_to_async

class BadmintonConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f'badminton_{self.match_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Always load the latest state from the DB
        current_state = await self.get_match_state_from_db()
        await self.send(text_data=json.dumps(current_state))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        # Always load the latest state from the DB
        state = await self.get_match_state_from_db()

        # Update state with incoming data
        state.update({
            k: v for k, v in data.items()
            if k in state and v is not None
        })

        await self.save_match_state_to_db(state)

        # Reload state from DB to ensure consistency
        updated_state = await self.get_match_state_from_db()
        await self.channel_layer.group_send(
            self.group_name,
            {'type': 'score_update', **updated_state, 'commentary': data.get('commentary', '')}
        )

    async def score_update(self, event):
        await self.send(text_data=json.dumps(event))

    @sync_to_async
    def get_match_state_from_db(self):
        try:
            match = Match.objects.get(id=self.match_id)
            return {
                "scoreA": match.score_team1,
                "scoreB": match.score_team2,
                "totalPoints": match.total_points,
                "matchStarted": match.status == Match.STATUS_LIVE,
                "pointsHistory": json.loads(match.points_history_json or '[]'),
                "team1_name": match.team1.name,
                "team2_name": match.team2.name,
                "player1_team1_name": match.player1_team1,
                "player2_team1_name": match.player2_team1,
                "player1_team2_name": match.player1_team2,
                "player2_team2_name": match.player2_team2,
                "matchEnded": match.status == Match.STATUS_COMPLETED,
                "winner": "A" if match.winner == match.team1 else ("B" if match.winner == match.team2 else None),
                "status": match.status,
            }
        except Match.DoesNotExist:
            return {
                "scoreA": 0, "scoreB": 0, "totalPoints": 21, "matchStarted": False,
                "pointsHistory": [], "team1_name": "Team A", "team2_name": "Team B",
                "player1_team1_name": "", "player2_team1_name": "",
                "player1_team2_name": "", "player2_team2_name": "",
                "matchEnded": False, "winner": None, "status": Match.STATUS_SCHEDULED
            }

    @sync_to_async
    def save_match_state_to_db(self, state):
        try:
            match = Match.objects.get(id=self.match_id)
            match.score_team1 = state['scoreA']
            match.score_team2 = state['scoreB']
            match.total_points = state['totalPoints']
            match.points_history_json = json.dumps(state['pointsHistory'])
            match.status = state['status']
            match.player1_team1 = state['player1_team1_name']
            match.player2_team1 = state['player2_team1_name']
            match.player1_team2 = state['player1_team2_name']
            match.player2_team2 = state['player2_team2_name']

            if state['winner'] == "A":
                match.winner = match.team1
            elif state['winner'] == "B":
                match.winner = match.team2
            else:
                match.winner = None

            match.save()
        except Exception as e:
            print(f"Error saving match state: {e}")
