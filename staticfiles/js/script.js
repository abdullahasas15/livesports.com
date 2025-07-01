document.addEventListener('DOMContentLoaded', function() {
    lucide.createIcons(); 
    
    const loginDropdown = document.getElementById('loginDropdown');
    const dropdownContent = document.querySelector('.dropdown-content');

    if (loginDropdown) {
        loginDropdown.addEventListener('click', function(event) {
            event.preventDefault();
            if (dropdownContent) {
                dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
            }
        });
    }

    window.addEventListener('click', function(event) {
        if (dropdownContent && !event.target.matches('#loginDropdown') && !event.target.matches('#loginDropdown *')) {
            if (dropdownContent.style.display === 'block') {
                dropdownContent.style.display = 'none';
            }
        }
    });

    // Removed specific event listeners for nav links as they are handled by Django URLs directly.
    // Removed generic event listeners for .btn.primary-btn and .btn.secondary-btn as they interfere with form submissions.

    // Example for "Get Started" and "Learn More" buttons (on home.html) - keep these if you intend to add specific JS behavior later
    // const getStartedBtn = document.querySelector('.btn.primary-btn');
    // if (getStartedBtn) {
    //     getStartedBtn.addEventListener('click', function(event) {
    //         console.log('Get Started button clicked!');
    //     });
    // }

    // const learnMoreBtn = document.querySelector('.btn.secondary-btn');
    // if (learnMoreBtn) {
    //     learnMoreBtn.addEventListener('click', function(event) {
    //         console.log('Learn More button clicked!');
    //     });
    // }
});
