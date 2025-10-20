// Main JavaScript file for Movem
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling to all links
    const links = document.querySelectorAll('a[href^="#"]');
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add loading animation delay for cards
    const cards = document.querySelectorAll('.movie-card, .actor-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
    });

    // Add image error handling for broken poster/photo URLs
    const images = document.querySelectorAll('img');
    images.forEach(img => {
        img.addEventListener('error', function() {
            if (this.classList.contains('card-img-top')) {
                if (this.closest('.actor-card')) {
                    this.src = 'https://via.placeholder.com/300x400/555/fff?text=No+Photo';
                } else {
                    this.src = 'https://via.placeholder.com/300x450/333/fff?text=No+Poster';
                }
            }
        });
    });

    // Add hover effect sound (optional - can be removed if not needed)
    const movieCards = document.querySelectorAll('.movie-card, .actor-card');
    movieCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});

// Function to handle responsive navigation
function toggleMobileNav() {
    const navbarCollapse = document.querySelector('.navbar-collapse');
    navbarCollapse.classList.toggle('show');
}

// Add click handlers for movie/actor cards (for future functionality)
function handleCardClick(type, id) {
    // This can be extended later for individual movie/actor pages
    console.log(`Clicked ${type} with ID: ${id}`);
}