// LiveSports JavaScript Functions

document.addEventListener("DOMContentLoaded", function () {
  // Initialize all interactive elements
  initializeTournamentNavigation();
  initializeCardAnimations();
  initializeGetStartedDropdown();

  console.log("LiveSports initialized successfully!");
});

// GET STARTED Dropdown Handler
function initializeGetStartedDropdown() {
  const getStartedBtn = document.getElementById("getStartedBtn");
  const dropdownMenu = document.getElementById("dropdownMenu");

  if (getStartedBtn && dropdownMenu) {
    getStartedBtn.addEventListener("click", function (e) {
      e.preventDefault();
      e.stopPropagation();
      dropdownMenu.classList.toggle("show");
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (e) {
      if (
        !getStartedBtn.contains(e.target) &&
        !dropdownMenu.contains(e.target)
      ) {
        dropdownMenu.classList.remove("show");
      }
    });

    // Close dropdown when pressing Escape
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        dropdownMenu.classList.remove("show");
      }
    });
  }
}

// Tournament Navigation Handler
function initializeTournamentNavigation() {
  const navTabs = document.querySelectorAll(".nav-tab");
  const tournamentCards = document.querySelectorAll(".tournament-card");

  navTabs.forEach((tab) => {
    tab.addEventListener("click", function () {
      const targetStatus = this.dataset.status;

      // Update active tab
      navTabs.forEach((t) => t.classList.remove("active"));
      this.classList.add("active");

      // Filter tournament cards
      filterTournamentCards(targetStatus);

      // Progress line removed
    });
  });
}

// Filter tournament cards based on status
function filterTournamentCards(status) {
  const allCards = document.querySelectorAll(".tournament-card");

  allCards.forEach((card, index) => {
    const cardStatus = card.dataset.status;

    if (cardStatus === status) {
      card.style.display = "block";
      card.style.animation = `slideUp 0.5s ease-out ${index * 0.1}s both`;
    } else {
      card.style.display = "none";
    }
  });
}

// Update progress line based on active tab - Removed (no progress dots)

// Initialize card hover animations
function initializeCardAnimations() {
  const cards = document.querySelectorAll(".tournament-card");

  cards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-8px)";
    });

    card.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0)";
    });
  });
}

// Initialize progress line - Removed (no progress dots)

// Utility function to show live score updates
function showLiveScoreUpdate(matchId, homeScore, awayScore) {
  const card = document.querySelector(`[data-match-id="${matchId}"]`);
  if (card) {
    const scoreElement = card.querySelector(".live-score");
    if (scoreElement) {
      scoreElement.textContent = `${homeScore} - ${awayScore}`;
      scoreElement.classList.add("animate-pulse");

      setTimeout(() => {
        scoreElement.classList.remove("animate-pulse");
      }, 2000);
    }
  }
}

// WebSocket connection for live updates
function initializeWebSocket() {
  const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = `${wsProtocol}//${window.location.host}/ws/scores/`;

  const socket = new WebSocket(wsUrl);

  socket.onopen = function (e) {
    console.log("WebSocket connection established");
  };

  socket.onmessage = function (e) {
    const data = JSON.parse(e.data);

    if (data.type === "score_update") {
      showLiveScoreUpdate(data.match_id, data.home_score, data.away_score);
    }
  };

  socket.onclose = function (e) {
    console.log("WebSocket connection closed");
    // Attempt to reconnect after 3 seconds
    setTimeout(initializeWebSocket, 3000);
  };

  socket.onerror = function (e) {
    console.error("WebSocket error:", e);
  };
}

// Initialize WebSocket if on tournament pages
if (
  window.location.pathname.includes("/scores/") ||
  window.location.pathname === "/"
) {
  initializeWebSocket();
}

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({
        behavior: "smooth",
        block: "start",
      });
    }
  });
});

// Feature item hover effects
document.querySelectorAll(".feature-item").forEach((item) => {
  item.addEventListener("mouseenter", function () {
    this.style.background =
      "linear-gradient(to right, rgba(124, 58, 237, 0.2), rgba(59, 130, 246, 0.2))";
  });

  item.addEventListener("mouseleave", function () {
    this.style.background =
      "linear-gradient(to right, rgba(124, 58, 237, 0.1), rgba(59, 130, 246, 0.1))";
  });
});

// Button click effects
document.querySelectorAll(".btn-primary").forEach((btn) => {
  btn.addEventListener("click", function () {
    this.style.transform = "scale(0.95)";
    setTimeout(() => {
      this.style.transform = "scale(1)";
    }, 150);
  });
});

// Live tournament pulse animation
setInterval(() => {
  const liveBadges = document.querySelectorAll(".status-badge.live");
  liveBadges.forEach((badge) => {
    badge.style.opacity = "0.7";
    setTimeout(() => {
      badge.style.opacity = "1";
    }, 500);
  });
}, 2000);
