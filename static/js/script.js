document.addEventListener('DOMContentLoaded', function() {
    // Get references to the dropdown button and content
    const loginDropdown = document.getElementById('loginDropdown');
    const dropdownContent = document.querySelector('.dropdown-content');

    // Toggle dropdown visibility on click
    if (loginDropdown) { // Check if element exists before adding listener
        loginDropdown.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent default link behavior
            if (dropdownContent) { // Ensure dropdownContent exists
                dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
            }
        });
    }

    // Close the dropdown if the user clicks outside of it
    window.addEventListener('click', function(event) {
        // Ensure dropdownContent exists and the click is outside dropdown
        if (dropdownContent && !event.target.matches('#loginDropdown') && !event.target.matches('#loginDropdown *')) {
            if (dropdownContent.style.display === 'block') {
                dropdownContent.style.display = 'none';
            }
        }
    });

    // --- REMOVED SPECIFIC EVENT LISTENERS FOR NAV LINKS ---
    // These links (adminLoginLink, ownerPanelLink, signupLink, logoutLink)
    // now use Django URLs directly via their href attributes in base.html.
    // Their JavaScript event listeners were causing errors because the elements
    // might not always exist or their IDs might be dynamically generated/removed.
    // The previous alerts/console.logs for these links are also removed.

    // Example for "Get Started" and "Learn More" buttons (on home.html)
    const getStartedBtn = document.querySelector('.btn.primary-btn');
    if (getStartedBtn) {
        getStartedBtn.addEventListener('click', function(event) {
            event.preventDefault();
            console.log('Get Started button clicked!');
        });
    }

    const learnMoreBtn = document.querySelector('.btn.secondary-btn');
    if (learnMoreBtn) {
        learnMoreBtn.addEventListener('click', function(event) {
            event.preventDefault();
            console.log('Learn More button clicked!');
        });
    }
});
