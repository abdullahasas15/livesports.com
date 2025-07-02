let pointsHistory = [];
let isMatchEnded = false;

let ws = null;

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

function updateUI() {
    document.getElementById('score').textContent = `${scoreA} - ${scoreB}`;
    document.getElementById('total-points').textContent = totalPoints;
    renderBoxes(pointsHistory, totalPoints);
    // Show winner if match ended
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
        status: isMatchEnded ? 'completed' : 'live'
    }));
}

function checkDeuceAndUpdate() {
    // If both teams reach totalPoints - 1, increase totalPoints by 1 (deuce)
    if (!isMatchEnded && scoreA === totalPoints - 1 && scoreB === totalPoints - 1) {
        totalPoints += 1;
        updateUI();
        sendUpdate({ commentary: `Deuce! Match extended to ${totalPoints} points.` });
        return true;
    }
    return false;
}

function checkAutoWin() {
    if (!isMatchEnded) {
        if (scoreA === totalPoints) {
            isMatchEnded = true;
            sendUpdate({ winner: "A", commentary: `Game over! ${team1Name} wins with a score of ${scoreA} - ${scoreB}!` });
            showEndMessage(team1Name);
            return true;
        } else if (scoreB === totalPoints) {
            isMatchEnded = true;
            sendUpdate({ winner: "B", commentary: `Game over! ${team2Name} wins with a score of ${scoreA} - ${scoreB}!` });
            showEndMessage(team2Name);
            return true;
        }
    }
    return false;
}

function connectWS() {
    ws = new WebSocket(wsUrl);

    ws.onopen = () => console.log("Admin WebSocket connected.");
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
        if (!checkDeuceAndUpdate()) {
            if (!checkAutoWin()) {
                sendUpdate({ commentary: `${team1Name} scored a point!` });
            }
        }
    };

    document.getElementById('teamB-plus').onclick = () => {
        if (isMatchEnded) return;
        scoreB++;
        pointsHistory.push("B");
        if (!checkDeuceAndUpdate()) {
            if (!checkAutoWin()) {
                sendUpdate({ commentary: `${team2Name} scored a point!` });
            }
        }
    };

    document.getElementById('win-teamA').onclick = () => {
        if (isMatchEnded) return;
        isMatchEnded = true;
        sendUpdate({ winner: "A", commentary: `Game over! ${team1Name} wins with a score of ${scoreA} - ${scoreB}!` });
        showEndMessage(team1Name);
    };

    document.getElementById('win-teamB').onclick = () => {
        if (isMatchEnded) return;
        isMatchEnded = true;
        sendUpdate({ winner: "B", commentary: `Game over! ${team2Name} wins with a score of ${scoreA} - ${scoreB}!` });
        showEndMessage(team2Name);
    };

    document.getElementById('post-commentary').onclick = () => {
        const commentary = document.getElementById('commentary-select').value;
        if (commentary) sendUpdate({ commentary });
    };
});