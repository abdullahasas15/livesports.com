document.addEventListener('DOMContentLoaded', function() {
    // Get references to the dropdown button and content
    const loginDropdown = document.getElementById('loginDropdown');
    const dropdownContent = document.querySelector('.dropdown-content');

    // Toggle dropdown visibility on click
    loginDropdown.addEventListener('click', function(event) {
        event.preventDefault(); // Prevent default link behavior
        dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
    });

    // Close the dropdown if the user clicks outside of it
    window.addEventListener('click', function(event) {
        if (!event.target.matches('#loginDropdown') && !event.target.matches('#loginDropdown *')) {
            if (dropdownContent.style.display === 'block') {
                dropdownContent.style.display = 'none';
            }
        }
    });

    // You can add event listeners to the actual links here for demonstration

    // The 'adminLoginLink' alert has been removed, as the link will now directly navigate via Django URL.

    document.getElementById('ownerPanelLink').addEventListener('click', function(event) {
        event.preventDefault();
        // Changed alert to console.log to avoid pop-ups during development
        console.log('Owner Panel clicked! (Implement your Django URL here)');
    });

    document.getElementById('signupLink').addEventListener('click', function(event) {
        event.preventDefault();
        // Changed alert to console.log
        console.log('Sign Up clicked! (Implement your Django URL here)');
    });

    // Example for "Get Started" and "Learn More" buttons
    document.querySelector('.btn.primary-btn').addEventListener('click', function(event) {
        event.preventDefault();
        // Changed alert to console.log
        console.log('Get Started button clicked!');
    });

    document.querySelector('.btn.secondary-btn').addEventListener('click', function(event) {
        event.preventDefault();
        // Changed alert to console.log
        console.log('Learn More button clicked!');
    });
});
