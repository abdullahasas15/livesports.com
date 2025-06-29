from channels.generic.websocket import AsyncWebsocketConsumer
import json
from apps.tournaments.models import Match, Team # Import Team model for winner
from asgiref.sync import sync_to_async

# In-memory dictionary for current match states.
# This serves as a cache and will be synchronized with the database.
match_states = {}

class BadmintonConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.group_name = f'badminton_{self.match_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        # Initialize current_state with a default BEFORE the try block
        # This ensures current_state is always defined, even if DB lookup fails
        current_state = {
            "scoreA": 0, "scoreB": 0, "totalPoints": 21, "matchStarted": False, "pointsHistory": [],
            "team1_name": "Team A", "team2_name": "Team B", "matchEnded": False, "winner": None,
            "status": Match.STATUS_SCHEDULED # Default status
        }

        try:
            # IMPORTANT: Wrap ORM calls with sync_to_async
            match = await sync_to_async(Match.objects.get)(id=self.match_id)
            current_state = { # Re-assign current_state if DB lookup is successful
                "scoreA": match.score_team1,
                "scoreB": match.score_team2,
                "totalPoints": match.total_points,
                "matchStarted": match.status == Match.STATUS_LIVE, # Use DB status
                "pointsHistory": json.loads(match.points_history_json or '[]'), # Safely load JSON or empty list
                "team1_name": match.team1.name,
                "team2_name": match.team2.name,
                "matchEnded": match.status == Match.STATUS_COMPLETED, # Use DB status
                "winner": match.winner.name if match.winner else None, # Send winner's name
                "status": match.status, # Send current status
            }
            # Only store in global cache if successfully retrieved from DB
            match_states[self.match_id] = current_state 
        except Match.DoesNotExist:
            print(f"Match with ID {self.match_id} not found. Keeping default state.")
            # current_state is already the default, so no change needed here.
            # Store default state in global cache if match was not found in DB
            match_states[self.match_id] = current_state 
        except Exception as e:
            print(f"Error loading match state on connect: {e}. Keeping default state.")
            # current_state is already the default, so no change needed here.
            # Store default state in global cache if error occurred
            match_states[self.match_id] = current_state

        # Send current state to newly connected client (current_state is guaranteed to be defined)
        await self.send(text_data=json.dumps(current_state))


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        match_id = self.match_id

        # Get the current state, ensure it exists or initialize defaults
        current_state = match_states.setdefault(match_id, {
            "scoreA": 0, "scoreB": 0, "totalPoints": 21, "matchStarted": False, "pointsHistory": [],
            "team1_name": "Team A", "team2_name": "Team B", "matchEnded": False, "winner": None,
            "status": Match.STATUS_SCHEDULED
        })

        # Update in-memory state based on received data
        # Only update if the data is present in the received payload
        if 'scoreA' in data: current_state["scoreA"] = data['scoreA']
        if 'scoreB' in data: current_state["scoreB"] = data['scoreB']
        if 'totalPoints' in data: current_state["totalPoints"] = data['totalPoints']
        if 'pointsHistory' in data: current_state["pointsHistory"] = data['pointsHistory']

        # Update match status and winner based on admin actions
        if data.get('matchStarted') is True:
            current_state["matchStarted"] = True
            current_state["matchEnded"] = False
            current_state["status"] = Match.STATUS_LIVE
            current_state["winner"] = None # Clear winner on new start
        elif data.get('matchStarted') is False and current_state["status"] == Match.STATUS_LIVE:
            # If admin explicitly sends matchStarted: false while it was live, it means reset
            current_state["matchStarted"] = False
            current_state["matchEnded"] = False
            current_state["scoreA"] = 0 # Reset scores
            current_state["scoreB"] = 0
            current_state["pointsHistory"] = [] # Clear history
            current_state["winner"] = None
            current_state["status"] = Match.STATUS_SCHEDULED # Back to scheduled
        elif data.get('matchEnded') is True:
            current_state["matchEnded"] = True
            current_state["matchStarted"] = False
            current_state["status"] = Match.STATUS_COMPLETED
            if data.get('winner'): # Winner should be 'A' or 'B' code from JS
                current_state["winner"] = data['winner'] # This will be 'A' or 'B'
            else:
                current_state["winner"] = None # Or handle draw/no winner scenario
        else: # If matchEnded is explicitly false or not present, and it's not the 'start' action
            if not current_state["matchStarted"] and not current_state["matchEnded"]:
                current_state["status"] = Match.STATUS_SCHEDULED # Default if not started/ended

        commentary = data.get('commentary', '')
        winner_team_code = data.get('winnerTeam', None) # 'A' or 'B' from JS when point scored

        # Dynamic commentary generation if no explicit commentary provided
        if not commentary and winner_team_code:
            # Fetch team names if not already known (should be from connect, but as a fallback)
            if not current_state.get("team1_name") or not current_state.get("team2_name"):
                try:
                    # IMPORTANT: Wrap ORM calls with sync_to_async
                    match = await sync_to_async(Match.objects.get)(id=self.match_id)
                    current_state["team1_name"] = match.team1.name
                    current_state["team2_name"] = match.team2.name
                except Match.DoesNotExist:
                    print(f"Match {self.match_id} not found while trying to get team names for commentary.")
                    current_state["team1_name"] = "Team A" # Fallback
                    current_state["team2_name"] = "Team B" # Fallback
                except Exception as e:
                    print(f"Error fetching team names in receive: {e}")
                    current_state["team1_name"] = "Team A" # Fallback
                    current_state["team2_name"] = "Team B" # Fallback

            if winner_team_code == "A":
                commentary = f"{current_state['team1_name']} scored a point!"
            elif winner_team_code == "B":
                commentary = f"{current_state['team2_name']} scored a point!"
        
        # If there's an explicit winner and matchEnded is true, craft the final commentary
        if current_state["matchEnded"] and current_state["winner"]:
            # 'winner' in current_state is already 'A' or 'B'
            winner_name_from_code = current_state["team1_name"] if current_state["winner"] == "A" else current_state["team2_name"]
            commentary = f"Game over! {winner_name_from_code} wins with a score of {current_state['scoreA']} - {current_state['scoreB']}!"
        elif current_state["matchEnded"] and not current_state["winner"]:
             commentary = f"Match ended with a score of {current_state['scoreA']} - {current_state['scoreB']}."


        # Persist state to database after every significant update
        await self.save_match_state_to_db(current_state)

        # Broadcast to group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'score_update',
                'scoreA': current_state["scoreA"],
                'scoreB': current_state["scoreB"],
                'totalPoints': current_state["totalPoints"],
                'commentary': commentary,
                'matchStarted': current_state["matchStarted"],
                'matchEnded': current_state["matchEnded"],
                'winner': current_state["winner"], # Send winner 'A' or 'B' code to client
                'pointsHistory': current_state["pointsHistory"],
                'team1_name': current_state["team1_name"],
                'team2_name': current_state["team2_name"],
            }
        )

    async def score_update(self, event):
        # This method is called when data needs to be sent to a client
        await self.send(text_data=json.dumps({
            'scoreA': event['scoreA'],
            'scoreB': event['scoreB'],
            'totalPoints': event['totalPoints'],
            'commentary': event['commentary'],
            'matchStarted': event['matchStarted'],
            'matchEnded': event['matchEnded'],
            'winner': event['winner'],
            'pointsHistory': event['pointsHistory'],
            'team1_name': event['team1_name'],
            'team2_name': event['team2_name'],
        }))

    @sync_to_async
    def save_match_state_to_db(self, state):
        """Saves the current match state to the Django database."""
        try:
            match = Match.objects.get(id=self.match_id)
            match.score_team1 = state.get("scoreA", 0)
            match.score_team2 = state.get("scoreB", 0)
            match.total_points = state.get("totalPoints", 21)
            match.points_history_json = json.dumps(state.get("pointsHistory", []))
            match.status = state.get("status", Match.STATUS_SCHEDULED)

            # Set winner FK (requires Team object, not just 'A' or 'B')
            winner_code = state.get("winner") # This is 'A' or 'B' from JS
            if winner_code == "A":
                match.winner = match.team1 # Set the actual Team object
            elif winner_code == "B":
                match.winner = match.team2 # Set the actual Team object
            else:
                match.winner = None # Clear winner if none

            match.save()
        except Match.DoesNotExist:
            print(f"Error: Match with ID {self.match_id} not found for saving state.")
        except Exception as e:
            print(f"Error saving match state to DB: {e}")
