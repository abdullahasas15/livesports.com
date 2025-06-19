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

    // --- REMOVED GENERIC EVENT LISTENERS FOR BUTTONS THAT PREVENT DEFAULT ---
    // These listeners were preventing proper form submission for buttons sharing these classes.
    // The "Get Started" and "Learn More" buttons should now rely on their href attributes or specific form logic.

    // Removed:
    // const getStartedBtn = document.querySelector('.btn.primary-btn');
    // if (getStartedBtn) {
    //     getStartedBtn.addEventListener('click', function(event) {
    //         event.preventDefault(); // This was the likely culprit for the create tournament button
    //         console.log('Get Started button clicked!');
    //     });
    // }

    // Removed:
    // const learnMoreBtn = document.querySelector('.btn.secondary-btn');
    // if (learnMoreBtn) {
    //     learnMoreBtn.addEventListener('click', function(event) {
    //         event.preventDefault();
    //         console.log('Learn More button clicked!');
    //     });
    // }
});
