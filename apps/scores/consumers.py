from channels.generic.websocket import AsyncWebsocketConsumer
import json
from apps.tournaments.models import Match
from asgiref.sync import sync_to_async
from apps.scores.models import KabaddiRaid

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
                "points_team1": match.points_team1,
                "points_team2": match.points_team2,
            }
        except Match.DoesNotExist:
            return {
                "scoreA": 0, "scoreB": 0, "totalPoints": None, "matchStarted": False,
                "pointsHistory": [], "team1_name": "Team A", "team2_name": "Team B",
                "player1_team1_name": "", "player2_team1_name": "",
                "player1_team2_name": "", "player2_team2_name": "",
                "matchEnded": False, "winner": None, "status": Match.STATUS_SCHEDULED,
                "points_team1": 0, "points_team2": 0,
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

            # Save points if provided
            if 'points_team1' in state and state['points_team1'] is not None:
                match.points_team1 = state['points_team1']
            if 'points_team2' in state and state['points_team2'] is not None:
                match.points_team2 = state['points_team2']

            match.save()
        except Exception as e:
            print(f"Error saving match state: {e}")

class VolleyballConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f'volleyball_{self.match_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        current_state = await self.get_match_state_from_db()
        await self.send(text_data=json.dumps(current_state))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        state = await self.get_match_state_from_db()
        state.update({
            k: v for k, v in data.items()
            if k in state and v is not None
        })
        await self.save_match_state_to_db(state)
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
            # Volleyball: up to 6 players per team
            state = {
                "scoreA": match.score_team1,
                "scoreB": match.score_team2,
                "totalPoints": match.total_points,
                "matchStarted": match.status == Match.STATUS_LIVE,
                "pointsHistory": json.loads(match.points_history_json or '[]'),
                "team1_name": match.team1.name,
                "team2_name": match.team2.name,
                "matchEnded": match.status == Match.STATUS_COMPLETED,
                "winner": "A" if match.winner == match.team1 else ("B" if match.winner == match.team2 else None),
                "status": match.status,
                "points_team1": match.points_team1,
                "points_team2": match.points_team2,
            }
            for p in range(1, 7):
                state[f"player{p}_team1_name"] = getattr(match, f"volleyball_player{p}_team1", "")
                state[f"player{p}_team2_name"] = getattr(match, f"volleyball_player{p}_team2", "")
            return state
        except Match.DoesNotExist:
            state = {
                "scoreA": 0, "scoreB": 0, "totalPoints": None, "matchStarted": False,
                "pointsHistory": [], "team1_name": "Team A", "team2_name": "Team B",
                "matchEnded": False, "winner": None, "status": Match.STATUS_SCHEDULED,
                "points_team1": 0, "points_team2": 0,
            }
            for p in range(1, 7):
                state[f"player{p}_team1_name"] = ""
                state[f"player{p}_team2_name"] = ""
            return state

    @sync_to_async
    def save_match_state_to_db(self, state):
        try:
            match = Match.objects.get(id=self.match_id)
            match.score_team1 = state['scoreA']
            match.score_team2 = state['scoreB']
            match.total_points = state['totalPoints']
            match.points_history_json = json.dumps(state['pointsHistory'])
            match.status = state['status']
            for p in range(1, 7):
                if f"player{p}_team1_name" in state:
                    setattr(match, f"volleyball_player{p}_team1", state[f"player{p}_team1_name"])
                if f"player{p}_team2_name" in state:
                    setattr(match, f"volleyball_player{p}_team2", state[f"player{p}_team2_name"])
            if state['winner'] == "A":
                match.winner = match.team1
            elif state['winner'] == "B":
                match.winner = match.team2
            else:
                match.winner = None
            if 'points_team1' in state and state['points_team1'] is not None:
                match.points_team1 = state['points_team1']
            if 'points_team2' in state and state['points_team2'] is not None:
                match.points_team2 = state['points_team2']
            match.save()
        except Exception as e:
            print(f"Error saving volleyball match state: {e}")

class TableTennisConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f'tabletennis_{self.match_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        current_state = await self.get_match_state_from_db()
        await self.send(text_data=json.dumps(current_state))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        state = await self.get_match_state_from_db()
        state.update({
            k: v for k, v in data.items()
            if k in state and v is not None
        })
        await self.save_match_state_to_db(state)
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
                "points_team1": match.points_team1,
                "points_team2": match.points_team2,
            }
        except Match.DoesNotExist:
            return {
                "scoreA": 0, "scoreB": 0, "totalPoints": None, "matchStarted": False,
                "pointsHistory": [], "team1_name": "Team A", "team2_name": "Team B",
                "player1_team1_name": "", "player2_team1_name": "",
                "player1_team2_name": "", "player2_team2_name": "",
                "matchEnded": False, "winner": None, "status": Match.STATUS_SCHEDULED,
                "points_team1": 0, "points_team2": 0,
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
            if 'points_team1' in state and state['points_team1'] is not None:
                match.points_team1 = state['points_team1']
            if 'points_team2' in state and state['points_team2'] is not None:
                match.points_team2 = state['points_team2']
            match.save()
        except Exception as e:
            print(f"Error saving table tennis match state: {e}")


class ThrowballConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f'throwball_{self.match_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        current_state = await self.get_match_state_from_db()
        await self.send(text_data=json.dumps(current_state))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        state = await self.get_match_state_from_db()
        state.update({
            k: v for k, v in data.items()
            if k in state and v is not None
        })
        await self.save_match_state_to_db(state)
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
            state = {
                "scoreA": match.score_team1,
                "scoreB": match.score_team2,
                "totalPoints": match.total_points,
                "matchStarted": match.status == Match.STATUS_LIVE,
                "pointsHistory": json.loads(match.points_history_json or '[]'),
                "team1_name": match.team1.name,
                "team2_name": match.team2.name,
                "matchEnded": match.status == Match.STATUS_COMPLETED,
                "winner": "A" if match.winner == match.team1 else ("B" if match.winner == match.team2 else None),
                "status": match.status,
                "points_team1": match.points_team1,
                "points_team2": match.points_team2,
            }
            for p in range(1, 10):
                state[f"player{p}_team1_name"] = getattr(match, f"throwball_player{p}_team1", "")
                state[f"player{p}_team2_name"] = getattr(match, f"throwball_player{p}_team2", "")
            return state
        except Match.DoesNotExist:
            state = {
                "scoreA": 0, "scoreB": 0, "totalPoints": None, "matchStarted": False,
                "pointsHistory": [], "team1_name": "Team A", "team2_name": "Team B",
                "matchEnded": False, "winner": None, "status": Match.STATUS_SCHEDULED,
                "points_team1": 0, "points_team2": 0,
            }
            for p in range(1, 10):
                state[f"player{p}_team1_name"] = ""
                state[f"player{p}_team2_name"] = ""
            return state

    @sync_to_async
    def save_match_state_to_db(self, state):
        try:
            match = Match.objects.get(id=self.match_id)
            match.score_team1 = state['scoreA']
            match.score_team2 = state['scoreB']
            match.total_points = state['totalPoints']
            match.points_history_json = json.dumps(state['pointsHistory'])
            match.status = state['status']
            for p in range(1, 10):
                if f"player{p}_team1_name" in state:
                    setattr(match, f"throwball_player{p}_team1", state[f"player{p}_team1_name"])
                if f"player{p}_team2_name" in state:
                    setattr(match, f"throwball_player{p}_team2", state[f"player{p}_team2_name"])
            if state['winner'] == "A":
                match.winner = match.team1
            elif state['winner'] == "B":
                match.winner = match.team2
            else:
                match.winner = None
            if 'points_team1' in state and state['points_team1'] is not None:
                match.points_team1 = state['points_team1']
            if 'points_team2' in state and state['points_team2'] is not None:
                match.points_team2 = state['points_team2']
            match.save()
        except Exception as e:
            print(f"Error saving throwball match state: {e}")
            
