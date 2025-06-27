const wsUrl = `ws://${window.location.host}/ws/badminton/${matchId}/`;
const socket = new WebSocket(wsUrl);

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    document.getElementById("score").innerText = `${data.scoreA} - ${data.scoreB}`;
    renderBoxes("teamA-points", totalPoints, data.scoreA, "green");
    renderBoxes("teamB-points", totalPoints, data.scoreB, "red");
};

function renderBoxes(containerId, total, score, colorClass) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";
    for (let i = 1; i <= total; i++) {
        const box = document.createElement("div");
        box.className = "point-box";
        if (score >= i) box.classList.add(colorClass);
        container.appendChild(box);
    }
}

document.getElementById("incrementA").onclick = () => {
    scoreA += 1;
    sendUpdate();
};
document.getElementById("incrementB").onclick = () => {
    scoreB += 1;
    sendUpdate();
};
document.getElementById("post-commentary").onclick = () => {
    sendUpdate();
};

function sendUpdate() {
    const commentary = document.getElementById("commentary-select").value;
    socket.send(JSON.stringify({
        scoreA: scoreA,
        scoreB: scoreB,
        totalPoints: totalPoints,
        commentary: commentary
    }));
}