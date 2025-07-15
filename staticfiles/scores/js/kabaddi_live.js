// Kabaddi Live JS

document.addEventListener('DOMContentLoaded', function() {
    // Get match_id from a global variable or data attribute
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

    // Placeholder player status (replace with backend data)
    let playerStatus = window.kabaddi_players_status || [
        {name: 'Player 1', status: 'in'},
        {name: 'Player 2', status: 'in'},
        {name: 'Player 3', status: 'in'},
        {name: 'Player 4', status: 'in'},
        {name: 'Player 5', status: 'in'},
        {name: 'Player 6', status: 'in'},
        {name: 'Player 7', status: 'in'},
        {name: 'Player 8', status: 'in'},
        {name: 'Player 9', status: 'in'},
        {name: 'Player 10', status: 'in'},
        {name: 'Player 11', status: 'in'},
        {name: 'Player 12', status: 'in'},
        {name: 'Player 13', status: 'in'},
        {name: 'Player 14', status: 'in'}
    ];

    function updateDisplay(data) {
        if (data.scoreA !== undefined && data.scoreB !== undefined) {
            document.getElementById('score-display').textContent = `${data.scoreA} - ${data.scoreB}`;
        }
        if (data.raid_log && data.raid_log.length > 0) {
            const lastRaid = data.raid_log[data.raid_log.length - 1];
            document.getElementById('current-raid').textContent = `Raid #${lastRaid.raid_number}`;
            document.getElementById('live-raider').textContent = lastRaid.raider;
            document.getElementById('live-defenders').textContent = lastRaid.defenders.join(', ');
            document.getElementById('live-last-action').textContent = lastRaid.result;
        }
        // Player status (from backend)
        const statusList = document.getElementById('player-status-list');
        if (data.player_status && statusList) {
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

    // WebSocket receive
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        updateDisplay(data);
    };

    socket.onclose = function() {
        console.warn('Kabaddi WebSocket closed.');
    };

    // Initial display (placeholder)
    updateDisplay({scoreA: 0, scoreB: 0, raid_log: []});
}); 