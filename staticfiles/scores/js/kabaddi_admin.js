// Kabaddi Admin JS

document.addEventListener('DOMContentLoaded', function() {
    // Get match_id from a data attribute or global variable
    let matchId = window.match_id;
    if (!matchId) {
        const el = document.getElementById('score-display');
        if (el && el.dataset.matchId) matchId = el.dataset.matchId;
    }
    if (!matchId) {
        console.error('No match_id found for WebSocket connection!');
        return;
    }
    const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const wsUrl = `${wsScheme}://${window.location.host}/ws/kabaddi/${matchId}/`;
    const socket = new WebSocket(wsUrl);

    // Placeholder player data (replace with backend data)
    const players = window.kabaddi_players || [
        'Player 1', 'Player 2', 'Player 3', 'Player 4', 'Player 5', 'Player 6', 'Player 7',
        'Player 8', 'Player 9', 'Player 10', 'Player 11', 'Player 12', 'Player 13', 'Player 14'
    ];

    // Populate raider and defenders dropdowns
    const raiderSelect = document.getElementById('raider-select');
    const defendersSelect = document.getElementById('defenders-select');
    players.forEach(p => {
        let opt = document.createElement('option');
        opt.value = p;
        opt.textContent = p;
        raiderSelect.appendChild(opt.cloneNode(true));
        defendersSelect.appendChild(opt);
    });

    // Timer logic
    let timer = 30;
    let timerInterval = null;
    const timerDisplay = document.getElementById('raid-timer');
    const startRaidBtn = document.getElementById('start-raid-btn');

    function updateTimerDisplay() {
        timerDisplay.textContent = `00:${timer < 10 ? '0' : ''}${timer}`;
    }

    function startTimer() {
        timer = 30;
        updateTimerDisplay();
        if (timerInterval) clearInterval(timerInterval);
        timerInterval = setInterval(() => {
            timer--;
            updateTimerDisplay();
            if (timer <= 0) {
                clearInterval(timerInterval);
                timerDisplay.textContent = 'Time Up!';
            }
        }, 1000);
    }

    startRaidBtn.addEventListener('click', startTimer);

    // Raid action buttons
    const logList = document.getElementById('raid-log-list');
    document.querySelectorAll('.raid-action-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const raider = raiderSelect.value;
            const defenders = Array.from(defendersSelect.selectedOptions).map(opt => opt.value);
            // Optionally, get points from UI if you have a field
            const scoreDisplay = document.getElementById('score-display');
            let [scoreA, scoreB] = scoreDisplay.textContent.split('-').map(s => parseInt(s.trim()));
            // Send to backend
            socket.send(JSON.stringify({
                action,
                raider,
                defenders,
                points_team1: scoreA,
                points_team2: scoreB,
                extra_info: {},
            }));
        });
    });

    // WebSocket receive
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        // Update score
        if (data.scoreA !== undefined && data.scoreB !== undefined) {
            document.getElementById('score-display').textContent = `${data.scoreA} - ${data.scoreB}`;
        }
        // Update log
        if (data.raid_log) {
            logList.innerHTML = '';
            data.raid_log.slice().reverse().forEach(raid => {
                const li = document.createElement('li');
                li.textContent = `#${raid.raid_number} [${raid.result}] Raider: ${raid.raider}, Defenders: ${raid.defenders.join(', ')}, Score: ${raid.points_team1} - ${raid.points_team2}`;
                logList.appendChild(li);
            });
        }
        // Update player status grid
        if (data.player_status) {
            const statusList = document.getElementById('player-status-list');
            if (statusList) {
                statusList.innerHTML = '';
                window.kabaddi_players.forEach(p => {
                    const div = document.createElement('div');
                    const status = data.player_status[p] || 'in';
                    div.className = 'player-status-item' + (status === 'out' ? ' out' : '');
                    div.textContent = p + (status === 'out' ? ' (Out)' : '');
                    statusList.appendChild(div);
                });
            }
        }
    };

    socket.onclose = function() {
        console.warn('Kabaddi WebSocket closed.');
    };
}); 