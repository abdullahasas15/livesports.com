let ws = null;
let matchEnded = false;

function renderBoxes(history, total) {
    const teamA = document.getElementById('teamA-points');
    const teamB = document.getElementById('teamB-points');
    teamA.innerHTML = teamB.innerHTML = '';

    for (let i = 0; i < total; i++) {
        const boxA = document.createElement('span');
        const boxB = document.createElement('span');
        boxA.className = boxB.className = 'point-box';
        if (history[i] === "A") {
            boxA.classList.add('green');
            boxB.classList.add('red');
        } else if (history[i] === "B") {
            boxA.classList.add('red');
            boxB.classList.add('green');
        }
        teamA.appendChild(boxA);
        teamB.appendChild(boxB);
    }
}

function updateUI(data) {
    document.getElementById('score').textContent = `${data.scoreA} - ${data.scoreB}`;
    document.getElementById('total-points').textContent = data.totalPoints;
    renderBoxes(data.pointsHistory || [], data.totalPoints);

    if (data.commentary) {
        document.getElementById('commentary').textContent = data.commentary;
    }

    if (data.matchEnded) {
        matchEnded = true;
        const winnerName = data.winner === "A" ? data.team1_name : data.winner === "B" ? data.team2_name : "No specific team";
        document.getElementById('live-container').style.opacity = 0.5;
        const msg = `Match Over! ${winnerName} Wins! Final Score: ${data.scoreA} - ${data.scoreB}`;
        document.getElementById('match-end-message').innerHTML = msg;
        document.getElementById('match-end-message').style.display = '';
    } else {
        matchEnded = false;
        document.getElementById('live-container').style.opacity = 1;
        document.getElementById('match-end-message').style.display = 'none';
    }
}

window.addEventListener('DOMContentLoaded', () => {
    const wsUrl = document.getElementById('ws-url').value;
    ws = new WebSocket(wsUrl);

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateUI(data);
    };

    ws.onclose = () => setTimeout(() => location.reload(), 3000);
});