let totalPoints = null;
let scoreA = 0;
let scoreB = 0;
let ws = null;
let pointsHistory = [];
let matchInProgress = false; // Controls the UI display for admin

// Utility to render the point boxes
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

// Function to display a custom alert message
function showCustomAlert(message) {
    const alertBox = document.createElement('div');
    alertBox.className = 'fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center';
    alertBox.innerHTML = `
        <div class="p-8 border shadow-lg rounded-md bg-white">
            <p class="text-gray-800 text-lg">${message}</p>
            <div class="flex justify-center mt-4">
                <button id="close-alert-btn" class="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-75">
                    OK
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(alertBox);

    document.getElementById('close-alert-btn').onclick = function() {
        document.body.removeChild(alertBox);
    };
}

// Check for match completion
function checkMatchEnd() {
    let winnerCode = null; // 'A' or 'B'
    if (scoreA >= totalPoints && (scoreA - scoreB >= 2 || totalPoints === 1)) {
        winnerCode = "A";
    } else if (scoreB >= totalPoints && (scoreB - scoreA >= 2 || totalPoints === 1)) {
        winnerCode = "B";
    }

    if (winnerCode) {
        // Disable controls
        document.getElementById('incrementA').disabled = true;
        document.getElementById('incrementB').disabled = true;
        document.getElementById('post-commentary').disabled = true;
        matchInProgress = false; // Match is no longer in progress from admin perspective

        // Send match ended state to server
        sendUpdate('', false, winnerCode, true); // matchEnded: true
        showCustomAlert(`Match ended! Team ${winnerCode === "A" ? team1Name : team2Name} wins with a score of ${scoreA} - ${scoreB}!`);

    } else {
        // If no winner, ensure buttons are enabled if matchInProgress
        if (matchInProgress) {
            document.getElementById('incrementA').disabled = false;
            document.getElementById('incrementB').disabled = false;
            document.getElementById('post-commentary').disabled = false;
        }
    }
    return winnerCode;
}

// Only show scoring section after admin sets points and clicks Start Match
document.getElementById('start-match-btn').onclick = function() {
    const input = document.getElementById('total-points-input');
    const val = parseInt(input.value);
    if (isNaN(val) || val < 1 || val > 99) {
        showCustomAlert("Please enter a valid number of points (1-99).");
        return;
    }
    totalPoints = val;
    scoreA = 0; // Reset scores for a new match
    scoreB = 0;
    pointsHistory = []; // Clear history for a new match
    matchInProgress = true; // Set match to in progress

    // Enable buttons
    document.getElementById('incrementA').disabled = false;
    document.getElementById('incrementB').disabled = false;
    document.getElementById('post-commentary').disabled = false;

    // Show scoring section
    document.getElementById('setup-section').style.display = 'none';
    document.getElementById('scoring-section').style.display = '';
    
    connectWS(); // Ensure WS is connected
    sendUpdate('', true, null, false); // Send matchStarted: true
    updateScore(); // Initial score display
};

function checkDeuceAndExtend() {
    // Only extend if both scores are at least (totalPoints - 1) and are equal
    if (scoreA === scoreB && scoreA >= totalPoints -1 && totalPoints > 1) { // totalPoints > 1 prevents extending for 1-point games
        totalPoints += 2; // Extend by 2 points
    }
}

// Increment Team A
document.getElementById('incrementA').onclick = function() {
    if (matchInProgress) { // Only allow if match is in progress
        scoreA++;
        pointsHistory.push("A");
        checkDeuceAndExtend();
        updateScore();
        const winner = checkMatchEnd(); // Check for winner after score update
        sendUpdate('', false, winner, winner !== null, "A"); // winner !== null means matchEnded: true
    }
};

// Increment Team B
document.getElementById('incrementB').onclick = function() {
    if (matchInProgress) { // Only allow if match is in progress
        scoreB++;
        pointsHistory.push("B");
        checkDeuceAndExtend();
        updateScore();
        const winner = checkMatchEnd(); // Check for winner after score update
        sendUpdate('', false, winner, winner !== null, "B"); // winner !== null means matchEnded: true
    }
};

// Post commentary
document.getElementById('post-commentary').onclick = function() {
    if (matchInProgress) { // Only allow if match is in progress
        const commentary = document.getElementById('commentary-select').value;
        if (commentary) {
            sendUpdate(commentary, false, null, false, null); // Only send commentary, not a point
            document.getElementById('commentary-select').selectedIndex = 0; // Reset dropdown
        }
    }
};

// Update score and boxes in UI
function updateScore() {
    document.getElementById('score').textContent = `${scoreA} - ${scoreB}`;
    renderBoxes(pointsHistory, totalPoints);
}

// WebSocket connection and handlers
function connectWS() {
    // Prevent multiple WebSocket connections
    if (ws && ws.readyState === WebSocket.OPEN) {
        console.log("WebSocket already open.");
        return;
    }
    
    ws = new WebSocket(wsUrl);

    ws.onopen = function() {
        console.log("Admin WebSocket connected.");
        // When reconnecting, send current known state to sync with server
        sendUpdate('', matchInProgress, checkMatchEnd(), checkMatchEnd() !== null);
    };

    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log("Admin WS received:", data);

        // Update core match data if provided by server
        // This is mainly for initial sync or if another admin makes changes
        if (typeof data.scoreA !== "undefined" && typeof data.scoreB !== "undefined") {
            scoreA = data.scoreA;
            scoreB = data.scoreB;
            totalPoints = data.totalPoints; // Update totalPoints from server (especially for deuce extension)
            pointsHistory = data.pointsHistory || [];
            updateScore(); // Re-render scores and boxes
        }

        // Handle match status changes from server (e.g., if another admin ends/resets)
        if (typeof data.matchEnded !== "undefined") {
            if (data.matchEnded) {
                matchInProgress = false;
                document.getElementById('incrementA').disabled = true;
                document.getElementById('incrementB').disabled = true;
                document.getElementById('post-commentary').disabled = true;
                showCustomAlert(`Match has ended! Final score: ${scoreA} - ${scoreB}. Winner: ${data.winner}!`);
                document.getElementById('setup-section').style.display = 'none'; // Keep admin in scoring view
                document.getElementById('scoring-section').style.display = ''; // But disable controls
            } else if (!data.matchStarted && !data.matchEnded) { // Match reset
                // Only reset UI if match was explicitly moved to scheduled from server
                matchInProgress = false;
                scoreA = 0;
                scoreB = 0;
                pointsHistory = [];
                totalPoints = null; // Reset total points so setup section shows
                document.getElementById('total-points-input').value = '';
                document.getElementById('setup-section').style.display = ''; // Show setup
                document.getElementById('scoring-section').style.display = 'none'; // Hide scoring
            } else if (data.matchStarted && !data.matchEnded) { // Match is live (started)
                matchInProgress = true;
                document.getElementById('setup-section').style.display = 'none';
                document.getElementById('scoring-section').style.display = '';
                document.getElementById('incrementA').disabled = false;
                document.getElementById('incrementB').disabled = false;
                document.getElementById('post-commentary').disabled = false;
            }
        }
        
        // Handle commentary (show only latest one)
        const commentaryLog = document.getElementById('commentary-log');
        commentaryLog.innerHTML = ''; // Clear existing commentary
        if (data.commentary) {
            const newCommentaryDiv = document.createElement('div');
            newCommentaryDiv.textContent = data.commentary; // Use textContent for safety
            commentaryLog.appendChild(newCommentaryDiv); // Append new commentary
        }
    };

    ws.onclose = function(event) {
        console.log("Admin WebSocket closed, code: " + event.code + ", reason: " + event.reason);
        // Only attempt to reconnect if not explicitly closed or on error
        if (!event.wasClean) {
            console.log("Admin WebSocket disconnected. Attempting to reconnect...");
            setTimeout(connectWS, 3000); // Try to reconnect after 3 seconds
        }
    };

    ws.onerror = function(error) {
        console.error("Admin WebSocket error:", error);
    };
}

// Send score and commentary to server
function sendUpdate(commentary, matchStarted = false, winner = null, matchEnded = false, winnerTeam = null) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        const payload = {
            scoreA: scoreA,
            scoreB: scoreB,
            totalPoints: totalPoints,
            commentary: commentary,
            matchStarted: matchStarted,
            winner: winner, // 'A' or 'B'
            matchEnded: matchEnded,
            winnerTeam: winnerTeam, // 'A' or 'B' for dynamic commentary generation
            pointsHistory: pointsHistory
        };
        console.log("Admin WS Sending:", payload);
        ws.send(JSON.stringify(payload));
    } else {
        console.warn("WebSocket not connected. Unable to send update. Attempting to reconnect...");
        connectWS(); // Attempt to reconnect if not connected
        // For crucial updates, you might queue them and send on open.
        // For now, this reconnect attempt should help.
    }
}


// Initialize UI state based on template values on page load
window.addEventListener('DOMContentLoaded', function() {
    // These variables are available globally from badminton_admin.html via template context
    // const matchId, wsUrl, initialScoreA, initialScoreB, initialTotalPoints (from input value)
    
    const initialPointsInput = document.getElementById('total-points-input');
    const scoreSpan = document.getElementById('score');

    // Attempt to parse existing match data from the Django template
    // This assumes the values like match.score_team1 are correctly populated.
    scoreA = parseInt(scoreSpan.textContent.split('-')[0].trim()) || 0;
    scoreB = parseInt(scoreSpan.textContent.split('-')[1].trim()) || 0;
    totalPoints = parseInt(initialPointsInput.value) || null; // totalPoints is initially from input

    // Only show scoring section if totalPoints is set (i.e., it's an existing match being edited)
    // and match.status from backend indicates it's LIVE or COMPLETED.
    // We can't directly get match.status here, so we rely on totalPoints being set.
    // If totalPoints is set AND (scoreA > 0 or scoreB > 0), assume it's an ongoing match.
    // Or simpler: if totalPoints has a value, we consider it "set up".
    if (totalPoints !== null && !isNaN(totalPoints) && totalPoints > 0) {
        matchInProgress = true;
        document.getElementById('setup-section').style.display = 'none';
        document.getElementById('scoring-section').style.display = '';
        updateScore(); // Display initial scores and boxes
        connectWS(); // Connect WebSocket immediately
        // Send initial state to ensure server (and other clients) are synced
        // This is important for refreshes on an ongoing match.
        // The server will respond with the full state.
        sendUpdate('', true, checkMatchEnd(), checkMatchEnd() !== null);
    } else {
        // For brand new matches, show the setup section.
        document.getElementById('setup-section').style.display = '';
        document.getElementById('scoring-section').style.display = 'none';
        matchInProgress = false;
    }
});

// Assuming these are passed from the Django template in badminton_admin.html
// const matchId = "{{ match.id }}";
// const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";
// const wsUrl = `${wsScheme}://${window.location.host}/ws/badminton/${matchId}/`;
// const team1Name = "{{ match.team1.name }}";
// const team2Name = "{{ match.team2.name }}";
