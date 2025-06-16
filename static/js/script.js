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
    document.getElementById('adminLoginLink').addEventListener('click', function(event) {
        event.preventDefault();
        alert('Admin Login clicked! (Implement your Django URL here)');
    });

    document.getElementById('ownerPanelLink').addEventListener('click', function(event) {
        event.preventDefault();
        alert('Owner Panel clicked! (Implement your Django URL here)');
    });

    document.getElementById('signupLink').addEventListener('click', function(event) {
        event.preventDefault();
        alert('Sign Up clicked! (Implement your Django URL here)');
    });

    // Example for "Get Started" and "Learn More" buttons
    document.querySelector('.btn.primary-btn').addEventListener('click', function(event) {
        event.preventDefault();
        alert('Get Started button clicked!');
    });

    document.querySelector('.btn.secondary-btn').addEventListener('click', function(event) {
        event.preventDefault();
        alert('Learn More button clicked!');
    });
});