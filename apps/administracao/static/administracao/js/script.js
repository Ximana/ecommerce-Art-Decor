document.addEventListener('DOMContentLoaded', function() {
    // Price range slider
    const priceRange = document.getElementById('priceRange');
    const minPriceLabel = document.getElementById('minPriceLabel');
    const maxPriceLabel = document.getElementById('maxPriceLabel');

    priceRange.addEventListener('input', function() {
        maxPriceLabel.textContent = `kz${this.value}`;
        console.log('Intervalo de preço alterado:', this.value);
    });

    // Search functionality
    const searchTrigger = document.querySelector('.search-trigger');
    const searchOverlay = document.getElementById('searchOverlay');
    const closeSearch = document.getElementById('closeSearch');

    searchTrigger.addEventListener('click', function(e) {
        e.preventDefault();
        searchOverlay.classList.add('active');
    });

    closeSearch.addEventListener('click', function() {
        searchOverlay.classList.remove('active');
    });

    // Close search overlay when clicking outside
    searchOverlay.addEventListener('click', function(e) {
        if (e.target === searchOverlay) {
            searchOverlay.classList.remove('active');
        }
    });
});