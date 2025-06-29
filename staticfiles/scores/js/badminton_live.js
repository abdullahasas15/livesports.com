// These variables are initialized from the template in badminton_live.html
// let totalPoints = {{ match.total_points }};
// let scoreA = {{ match.score_team1 }};
// let scoreB = {{ match.score_team2 }};
// let matchStarted = false; // Initialized in badminton_live.html as well
// let team1Name = "{{ match.team1.name }}"; // Get team names from template
// let team2Name = "{{ match.team2.name }}";

let pointsHistory = []; // This will be updated via WebSocket

// This is the correct renderBoxes function.
function renderBoxes(pointsHistory, total) {
    const teamA = document.getElementById('teamA-points');
    const teamB = document.getElementById('teamB-points');
    teamA.innerHTML = '';
    teamB.innerHTML = '';
    for (let i = 0; i < total; i++) {
        let boxA = document.createElement('span');
        let boxB = document.createElement('span');
        boxA.className = 'point-box';
        boxB.className = 'point-box';
        if (pointsHistory[i] === "A") {
            boxA.classList.add('green');
            boxB.classList.add('red');
        } else if (pointsHistory[i] === "B") {
            boxA.classList.add('red');
            boxB.classList.add('green');
        }
        teamA.appendChild(boxA);
        teamB.appendChild(boxB);
    }
}

function updateScore() {
    document.getElementById('score').textContent = `${scoreA} - ${scoreB}`;
    renderBoxes(pointsHistory, totalPoints);
}

function showWaitingUI() {
    document.getElementById('waiting-message').style.display = '';
    document.getElementById('viewer-container').style.display = 'none';
    document.getElementById('match-end-message').style.display = 'none';
}

function showViewerUI() {
    document.getElementById('waiting-message').style.display = 'none';
    document.getElementById('viewer-container').style.display = '';
    document.getElementById('match-end-message').style.display = 'none'; // Hide end message
}

function showMatchEndUI(winnerName) {
    document.getElementById('viewer-container').style.display = 'none';
    document.getElementById('waiting-message').style.display = 'none';
    const endMessageDiv = document.getElementById('match-end-message');
    endMessageDiv.innerHTML = `Match Over! ${winnerName || 'No winner specified.'} Wins! Final Score: ${scoreA} - ${scoreB}`;
    endMessageDiv.style.display = '';
}

// WebSocket connection and handlers
function connectWS() {
    // Only create a new WebSocket if one doesn't exist or is closed/closing
    if (typeof ws === 'undefined' || ws === null || ws.readyState === WebSocket.CLOSED || ws.readyState === WebSocket.CLOSING) {
        ws = new WebSocket(wsUrl);
    } else if (ws.readyState === WebSocket.OPEN) {
        console.log("Viewer WebSocket already open.");
        return; // Already connected
    }
    
    ws.onopen = function() {
        console.log("Viewer WebSocket connected.");
        // No need to send anything on open for viewer, just listen
    };

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log("Viewer WS received:", data);

        // Update core match data
        if (typeof data.scoreA !== "undefined") {
            scoreA = data.scoreA;
            scoreB = data.scoreB;
            totalPoints = data.totalPoints; // Update totalPoints as it might change due to deuce
            pointsHistory = data.pointsHistory || [];
            updateScore();
        }

        // Handle match started/ended state
        if (data.matchEnded) {
            matchStarted = false; // Match is no longer in progress
            const winnerName = data.winner ? (data.winner === "A" ? team1Name : team2Name) : 'No specific team';
            showMatchEndUI(winnerName);
        } else if (data.matchStarted) { // Match is live
            matchStarted = true;
            showViewerUI();
        } else { // Match is scheduled/reset
            matchStarted = false;
            showWaitingUI();
        }

        // Handle commentary (dynamic and no scrolling)
        const commentaryLog = document.getElementById('commentary-log');
        commentaryLog.innerHTML = ''; // Clear previous commentary
        let displayedCommentary = '';

        if (data.commentary) {
            displayedCommentary = data.commentary; // Use explicit commentary if provided
        }
        // No need for dynamic commentary generation on viewer side, as consumer now handles it.
        // The consumer will send either an explicit comment or a dynamically generated one.

        if (displayedCommentary) {
            const newCommentaryDiv = document.createElement('div');
            newCommentaryDiv.textContent = displayedCommentary;
            commentaryLog.appendChild(newCommentaryDiv);
        }
    };
    ws.onclose = function(event) {
        console.log("Viewer WebSocket closed, code: " + event.code + ", reason: " + event.reason);
        if (!event.wasClean) { // Attempt to reconnect only if connection wasn't cleanly closed
            console.log("Viewer WebSocket disconnected. Attempting to reconnect...");
            setTimeout(connectWS, 3000); // Try to reconnect after 3 seconds
        }
    };
    ws.onerror = function(error) {
        console.error("Viewer WebSocket error:", error);
    };
}

// Initial render and connect
window.addEventListener('DOMContentLoaded', function() {
    // Initialize UI state based on the 'matchStarted' flag passed from Django template
    // This helps in cases where the page refreshes during an already started match.
    if (matchStarted) { // matchStarted is a global var from badminton_live.html
        showViewerUI();
        updateScore(); // Initial score render
    } else {
        showWaitingUI();
    }
    connectWS();
});

// Declared in badminton_live.html
// const matchId = "{{ match.id }}";
// const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
// const wsUrl = `${wsScheme}://${window.location.host}/ws/badminton/${matchId}/`;
// let totalPoints = {{ match.total_points|default:21 }};
// let scoreA = {{ match.score_team1|default:0 }};
// let scoreB = {{ match.score_team2|default:0 }};
// let matchStarted = false;
// const team1Name = "{{ match.team1.name }}";
// const team2Name = "{{ match.team2.name }}";
