// Table Tennis Admin JS - based on volleyball_admin.js
// ... Will be filled with adapted code ...

let pointsHistory = [];
let isMatchEnded = false;

let ws = null;

function renderBoxes(history, total) {
    const teamA = document.getElementById('teamA-points');
    const teamB = document.getElementById('teamB-points');
    teamA.innerHTML = teamB.innerHTML = '';

    let numBoxes = total * 2;
    if (history.length > numBoxes) {
        numBoxes = Math.ceil((history.length - numBoxes) / 5) * 5 + numBoxes;
    }

    for (let i = 0; i < numBoxes; i++) {
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

function updateUI() {
    document.getElementById('score').textContent = `${scoreA} - ${scoreB}`;
    document.getElementById('total-points').textContent = totalPoints;
    renderBoxes(pointsHistory, totalPoints);
    if (isMatchEnded) {
        const winner = scoreA === totalPoints ? team1Name : scoreB === totalPoints ? team2Name : null;
        showEndMessage(winner);
    }
}

function showEndMessage(winner) {
    document.getElementById('admin-container').style.opacity = '0.5';
    const msgDiv = document.getElementById('match-end-message');
    msgDiv.innerHTML = `Match Over! ${winner || 'No specific team'} Wins! Final Score: ${scoreA} - ${scoreB}`;
    msgDiv.style.display = '';
}

function showPointsModal(winner) {
    const modal = document.getElementById('points-modal');
    const team1Span = document.getElementById('modal-team1-name');
    const team2Span = document.getElementById('modal-team2-name');
    const pointsTeam1Input = document.getElementById('points-team1');
    const pointsTeam2Input = document.getElementById('points-team2');
    team1Span.textContent = team1Name;
    team2Span.textContent = team2Name;
    if (winner === 'A') {
        pointsTeam1Input.value = 2;
        pointsTeam2Input.value = 0;
    } else if (winner === 'B') {
        pointsTeam1Input.value = 0;
        pointsTeam2Input.value = 2;
    } else {
        pointsTeam1Input.value = 0;
        pointsTeam2Input.value = 0;
    }
    modal.style.display = 'flex';
    setTimeout(() => pointsTeam1Input.focus(), 100);

    document.getElementById('points-modal-done').onclick = function() {
        modal.style.display = 'none';
        const pts1 = parseInt(pointsTeam1Input.value) || 0;
        const pts2 = parseInt(pointsTeam2Input.value) || 0;
        sendUpdate({ points_team1: pts1, points_team2: pts2, winner });
        showEndMessage(winner === 'A' ? team1Name : winner === 'B' ? team2Name : null);
    };
}

function checkAutoWin() {
    if (!isMatchEnded) {
        if (scoreA === totalPoints - 1 && scoreB === totalPoints - 1) {
            totalPoints += 2;
            updateUI();
            return false;
        }
        if (scoreA === totalPoints) {
            isMatchEnded = true;
            showPointsModal('A');
            return true;
        } else if (scoreB === totalPoints) {
            isMatchEnded = true;
            showPointsModal('B');
            return true;
        }
    }
    return false;
}

function connectWS() {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => console.log("Table Tennis Admin WebSocket connected.");
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (typeof data.scoreA === "number") scoreA = data.scoreA;
        if (typeof data.scoreB === "number") scoreB = data.scoreB;
        if (typeof data.totalPoints === "number") totalPoints = data.totalPoints;
        if (Array.isArray(data.pointsHistory)) pointsHistory = data.pointsHistory;
        isMatchEnded = !!data.matchEnded;
        updateUI();
        if (isMatchEnded) {
            const winner = data.winner === "A" ? team1Name : data.winner === "B" ? team2Name : null;
            showEndMessage(winner);
        }
    };
    ws.onclose = () => setTimeout(connectWS, 3000);
    ws.onerror = (err) => console.error("WebSocket error:", err);
}

window.addEventListener('DOMContentLoaded', () => {
    updateUI();
    connectWS();

    document.getElementById('teamA-plus').onclick = () => {
        if (isMatchEnded) return;
        scoreA++;
        pointsHistory.push("A");
        if (!checkAutoWin()) {
            sendUpdate({ commentary: `${team1Name} scored a point!` });
        }
    };

    document.getElementById('teamB-plus').onclick = () => {
        if (isMatchEnded) return;
        scoreB++;
        pointsHistory.push("B");
        if (!checkAutoWin()) {
            sendUpdate({ commentary: `${team2Name} scored a point!` });
        }
    };

    document.getElementById('win-teamA').onclick = () => {
        if (isMatchEnded) return;
        isMatchEnded = true;
        showPointsModal('A');
    };

    document.getElementById('win-teamB').onclick = () => {
        if (isMatchEnded) return;
        isMatchEnded = true;
        showPointsModal('B');
    };

    document.getElementById('post-commentary').onclick = () => {
        const commentary = document.getElementById('commentary-select').value;
        if (commentary) sendUpdate({ commentary });
    };

    const commentarySelect = document.getElementById('commentary-select');
    if (commentarySelect) {
        commentarySelect.style.display = '';
        commentarySelect.innerHTML = `
            <option value="">Select Commentary</option>
            <option value="Brilliant rally by ${team1Name}!">Brilliant rally by ${team1Name}!</option>
            <option value="Great serve, ${team2Name} scores!">Great serve, ${team2Name} scores!</option>
            <option value="Unforced error by ${team1Name}.">Unforced error by ${team1Name}.</option>
            <option value="${team2Name} dominates the table!">${team2Name} dominates the table!</option>
        `;
    }
});

function sendUpdate(extra = {}) {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({
        scoreA,
        scoreB,
        totalPoints,
        pointsHistory,
        matchStarted: true,
        matchEnded: isMatchEnded,
        winner: extra.winner || null,
        commentary: extra.commentary || "",
        status: isMatchEnded ? 'completed' : 'live',
        points_team1: extra.points_team1,
        points_team2: extra.points_team2
    }));
}
