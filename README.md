# LiveSports.com

LiveSports is a Django + Channels sports tournament platform with real-time match scoring over WebSockets.

## What this project does

- Admins create tournaments, teams, and sport-specific matches.
- Viewers browse tournaments and see live score updates.
- Match state is stored in PostgreSQL and pushed to connected clients instantly through WebSockets.

## Tech stack

- Django for backend and templates
- Django Channels for WebSocket support
- Daphne as the ASGI server
- PostgreSQL for persistent match data
- Vanilla JavaScript on the frontend for live score updates

## Project apps

| App | Responsibility |
| --- | --- |
| home | Landing page |
| viewer | Viewer signup, login, profile, and tournament browsing |
| adminpanel | Admin auth, tournament creation, and match configuration |
| tournaments | Core models: Game, Tournament, Team, Match, UserProfile |
| scores | Live match pages and WebSocket consumers |
| owner | Placeholder app |

## Environment setup

This repository now reads database settings from a local .env file.

Important values:

- DB host: db.vudtqivtknczdfkxikri.supabase.co
- DB port: 5432
- DB name: postgres
- DB user: postgres

The restored database already contains the data. Do not create new tables again unless the schema changes.

If Django asks for migrations on an already-restored database, use fake migrations instead of recreating tables.

## How the backend works

### 1) Authentication flow

- Admin sign up and login are handled in `apps/adminpanel/views.py`.
- Viewer sign up and login are handled in `apps/viewer/views.py`.
- Staff users are used for tournament and match management.
- Regular users are used for browsing and viewing live scores.

### 2) Tournament flow

1. An admin creates a tournament in the admin panel.
2. The app saves the tournament and creates teams.
3. The admin configures matches for each game.
4. Each match stores teams, player names, score fields, status, winner, and JSON score history.

### 3) Live score flow

1. Admin and viewer pages open a WebSocket connection for a match.
2. The consumer loads the current match state from PostgreSQL.
3. When score changes arrive, the consumer updates the `Match` row.
4. The updated state is broadcast to everyone in the same channel group.
5. The browser updates the page without a refresh.

## WebSocket architecture

WebSocket routes are defined per sport:

- Badminton
- Volleyball
- Table Tennis
- Throwball
- Kabaddi route exists in routing

The core consumer pattern is:

```python
async def connect(self):
	await self.channel_layer.group_add(self.group_name, self.channel_name)
	await self.accept()
	current_state = await self.get_match_state_from_db()
	await self.send(text_data=json.dumps(current_state))
```

```python
async def receive(self, text_data):
	data = json.loads(text_data)
	state = await self.get_match_state_from_db()
	state.update({k: v for k, v in data.items() if k in state and v is not None})
	await self.save_match_state_to_db(state)
	await self.channel_layer.group_send(self.group_name, {'type': 'score_update', **state})
```

### Why this design works

- The database is the source of truth.
- WebSocket messages are only the real-time delivery mechanism.
- If a client reconnects, it gets the latest state from the database immediately.

## Important functions to know for interview prep

### `apps.adminpanel.views.user_auth_view()`

Handles both admin login and signup in one place.

### `apps.adminpanel.views.create_tournament_view()`

Creates a tournament and its teams inside a transaction.

### `apps.adminpanel.views.manage_matches_view()`

Builds match configurations for each selected game.

### `apps.viewer.views.viewer_tournament_details_view()`

Computes the points table and prepares match data for the viewer page.

### `apps.scores.consumers.*Consumer`

Each consumer loads match state, saves updates, and broadcasts changes to the group.

## Key data model

The `Match` model stores:

- tournament and game relation
- team1 and team2
- score fields
- match status
- winner
- total points
- player names per sport
- `points_history_json`
- description

This makes the match row the central state record for both admin control and live viewer updates.

## ASGI and Daphne

- `livesports_project.asgi` routes HTTP requests to Django and WebSocket requests to Channels.
- `livesports_project.routing` collects the WebSocket routes.
- Daphne runs the ASGI application using the Procfile entry.

## Interview talking points

### Strengths

- Clear separation of admin and viewer flows
- Real-time score sync with persistent database state
- Sport-specific WebSocket consumers
- Reconnect-friendly architecture because the database is the source of truth

### Trade-offs

- In-memory channel layer is fine for single-process development, but not ideal for scale.
- Match player names are stored in explicit fields, which is easy to render but less flexible than JSON.
- Score history is stored as JSON text, which is good for replay but harder to query.

### Current implementation notes

- The Kabaddi WebSocket route is registered, but the consumer implementation still needs to be added or wired in.
- Some match-configuration code reuses repeated sport-field patterns, so it is worth reviewing carefully before production.

### What to say in an interview

You can describe this project as a Django tournament platform where admins configure matches, scores are stored in PostgreSQL, and WebSockets keep viewers synchronized in real time through Channels and Daphne.

## Local run notes

Use the local .env file for database settings and start the server with Daphne.

If the database already exists after restore, keep migrations fake so Django does not recreate tables.

## One-line summary

LiveSports is a multi-sport tournament management system with real-time match scoring, staff/admin workflows, viewer pages, and database-backed WebSocket synchronization.

## Backend Workflow Deep Dive (Interview Ready)

This section explains how backend logic works in real request order, with code snippets from your project.

### 1) Match creation workflow (admin)

Main entry point:

- `apps/adminpanel/views.py` -> `manage_matches_view(request, tournament_id)`

What happens:

1. It loads the admin's tournament and selected games.
2. Reads posted match rows per game.
3. Computes next `match_number` safely.
4. Builds `match_kwargs` with sport-specific fields.
5. Writes each match with `Match.objects.create(**match_kwargs)` inside a DB transaction.

Core snippet:

```python
with transaction.atomic():
	for game_obj in tournament_games:
		num_matches = int(request.POST.get(f'num_matches_{game_obj.id}', 0))
		used_match_numbers = set(
			Match.objects.filter(tournament=tournament, game=game_obj)
			.values_list('match_number', flat=True)
		)

		for i in range(1, num_matches + 1):
			team1_id = request.POST.get(f'game_{game_obj.id}_match_{i}_team1')
			team2_id = request.POST.get(f'game_{game_obj.id}_match_{i}_team2')
			if not team1_id or not team2_id:
				continue

			next_match_number = 1
			while next_match_number in used_match_numbers:
				next_match_number += 1
			used_match_numbers.add(next_match_number)

			match_kwargs = {
				'tournament': tournament,
				'game': game_obj,
				'match_number': next_match_number,
				'team1': get_object_or_404(Team, id=team1_id),
				'team2': get_object_or_404(Team, id=team2_id),
			}
			Match.objects.create(**match_kwargs)
```

Why this is good:

- `transaction.atomic()` protects from partial saves.
- `match_number` uniqueness per game/tournament is maintained.
- Sport fields are injected dynamically before create.

### 2) Match update workflow (admin scoring)

Match state is updated through WebSocket consumers, not normal POST forms.

Main file:

- `apps/scores/consumers.py`

Pattern used by each sport consumer:

1. `connect()` joins a match-specific channel group.
2. Current DB state is sent immediately to the client.
3. `receive()` merges incoming payload with DB state.
4. DB row is updated.
5. Updated state is broadcast to all clients in the same match group.

Connect + initial state snippet:

```python
async def connect(self):
	self.match_id = self.scope['url_route']['kwargs']['match_id']
	self.group_name = f'badminton_{self.match_id}'

	await self.channel_layer.group_add(self.group_name, self.channel_name)
	await self.accept()

	current_state = await self.get_match_state_from_db()
	await self.send(text_data=json.dumps(current_state))
```

Receive + save + broadcast snippet:

```python
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
```

DB persistence snippet:

```python
@sync_to_async
def save_match_state_to_db(self, state):
	match = Match.objects.get(id=self.match_id)
	match.score_team1 = state['scoreA']
	match.score_team2 = state['scoreB']
	match.total_points = state['totalPoints']
	match.points_history_json = json.dumps(state['pointsHistory'])
	match.status = state['status']
	match.save()
```

Inside this WebSocket code (line-by-line meaning):

- `async def ...`: this function runs in async mode, so it can pause without blocking other users.
- `await ...`: pause this function until that async operation finishes, then continue.
- `self.scope['url_route']['kwargs']['match_id']`: reads URL parameters from the WS route.
- `self.group_name = f'badminton_{self.match_id}'`: creates a room name per match.
- `await self.channel_layer.group_add(...)`: join this connection to the match room.
- `await self.accept()`: complete WebSocket handshake; without this, socket is not fully open.
- `await self.get_match_state_from_db()`: fetch latest DB state so reconnecting clients get current data.
- `await self.send(...)`: send current state JSON to that one connected client.
- `state.update(...)`: merge incoming payload into allowed fields only.
- `await self.save_match_state_to_db(state)`: persist score/status changes into PostgreSQL.
- `await self.channel_layer.group_send(...)`: broadcast one event to everyone in same match room.
- `'type': 'score_update'`: tells Channels which consumer method to call for the event.

How broadcast reaches each user:

```python
async def score_update(self, event):
	await self.send(text_data=json.dumps(event))
```

Why `@sync_to_async` is used:

- Django ORM calls are synchronous.
- Consumer methods are asynchronous.
- `@sync_to_async` safely runs DB work from async consumers without blocking the event loop.

Short interview explanation:

"In `connect()`, I join a match-specific Channels group and push the latest DB state immediately. In `receive()`, I merge incoming updates, save to DB, then broadcast via `group_send`, and each client receives that event in `score_update()` in real time."

### 3) Viewer live update workflow

Viewer pages are regular Django templates, then JS connects to WS endpoints.

Flow:

1. Viewer opens route like `/scores/badminton/live/<match_id>/`.
2. Browser JS opens `/ws/badminton/<match_id>/`.
3. Consumer sends current state from DB.
4. Every admin score action is pushed to same group.
5. Viewer UI updates without refresh.

Result: admin and viewers stay in sync in real time.

### 4) URL and routing pipeline (HTTP + WebSocket)

HTTP app router:

- `livesports_project/urls.py`

WebSocket router:

- `apps/scores/routing.py`

ASGI entry:

- `livesports_project/asgi.py`

ASGI snippet:

```python
application = ProtocolTypeRouter({
	"http": django_asgi_application,
	"websocket": AuthMiddlewareStack(
		URLRouter(websocket_urlpatterns)
	),
})
```

Meaning:

- Normal HTTP goes to Django views.
- WebSocket traffic goes to Channels consumers.
- Both run in same Daphne ASGI server.

### 5) Data model that powers the full flow

Main model:

- `apps/tournaments/models.py` -> `Match`

Important fields for backend logic:

- Teams: `team1`, `team2`
- Score: `score_team1`, `score_team2`
- Match state: `status`, `winner`
- Scoring config: `total_points`, `points_team1`, `points_team2`
- Replay/state: `points_history_json`
- Sport player fields: badminton/table tennis/volleyball/throwball/kabaddi player names

This single table acts as the source of truth for both admin control and live viewer rendering.

### 6) End-to-end sequence (easy to explain in interview)

1. Admin creates tournament and teams.
2. Admin configures matches per sport.
3. Match rows are saved in PostgreSQL.
4. Admin opens scoring screen and sends live updates via WebSocket.
5. Consumer persists updates to DB and broadcasts to group.
6. Viewer clients subscribed to same match group receive updates instantly.
7. Reconnected clients always recover latest state from DB on connect.

### 7) One-line interview pitch

"I built a Django + Channels system where match creation is transactional in HTTP views, and live scoring is stateful through WebSocket consumers that persist every update to PostgreSQL and broadcast to all match subscribers in real time."
