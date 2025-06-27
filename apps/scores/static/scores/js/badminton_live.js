const wsUrl = `ws://${window.location.host}/ws/badminton/${matchId}/`;
const socket = new WebSocket(wsUrl);

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    document.getElementById("score").innerText = `${data.scoreA} - ${data.scoreB}`;
    renderBoxes("teamA-points", data.totalPoints, data.scoreA, "green");
    renderBoxes("teamB-points", data.totalPoints, data.scoreB, "red");

    const comm = document.getElementById("commentary");
    comm.innerHTML = `<p>${data.commentary}</p>` + comm.innerHTML;
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