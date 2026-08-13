
function scrollFilters(distance) {
    const row = document.getElementById('filterScrollRow');
    // .scrollBy moves the scrollbar by the specified pixel amount
    row.scrollBy({
        left: distance,
        behavior: 'smooth'
    });
}

function scrollStoreProducts(distance) {
    const container = document.querySelector('.et-product-slider-wrapper');
    if (container) {
        container.scrollBy({
            left: distance,
            behavior: 'smooth'
        });
    }
}


// function to accept 3 sections
function scrollRoster(wrapperId, distance) {
    const container = document.getElementById(wrapperId);
    if (container) {
        container.scrollBy({
            left: distance,
            behavior: 'smooth'
        });
    }
}



// Advert Section Slider

let currentAd = 0;

function showNextAd() {
    const slider = document.querySelector('.advert-slider');
    const totalAds = document.querySelectorAll('.advert-item').length;
    currentAd = (currentAd + 1) % totalAds;
    slider.style.transform = `translateX(-${currentAd * 100}%)`;
}

// rotate every 5 seconds
setInterval(showNextAd, 5000);



const grid = document.querySelector('.product-roster-grid');
const dotsContainer = document.querySelector('.product-roster-dots');

// Calculate how many "columns" exist
const totalColumns = Math.ceil(grid.children.length / 3); // 3 rows per column

// Create dots
for (let i = 0; i < totalColumns; i++) {
    const dot = document.createElement('span');
    if (i === 0) dot.classList.add('active');
    dotsContainer.appendChild(dot);
}

// Update active dot on scroll
grid.addEventListener('scroll', () => {
    const columnWidth = grid.scrollWidth / totalColumns;
    const currentColumn = Math.round(grid.scrollLeft / columnWidth);
    document.querySelectorAll('.product-roster-dots span').forEach((dot, index) => {
        dot.classList.toggle('active', index === currentColumn);
    });
});







const searchInput = document.getElementById('searchInput');
const resultsContent = document.getElementById('resultsContent');
let debounceTimer;

searchInput.addEventListener('input', function() {
    const query = this.value.trim();

    // Clear the timer so we don't search while the user is still typing
    clearTimeout(debounceTimer);

    // If input is cleared, remove results
    if (query.length === 0) {
        resultsContent.innerHTML = "";
        return;
    }

    // Read the compiled URL cleanly from the HTML data attribute
    const baseSearchUrl = searchInput.getAttribute('data-search-url');

    // Wait 300ms after the last keystroke before hitting the database
    debounceTimer = setTimeout(() => {
        resultsContent.style.opacity = "0.9";

        // Construct the full fetch endpoint safely
        fetch(baseSearchUrl + "?s=" + encodeURIComponent(query))
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newResults = doc.querySelector('.rd-search-results');

                if (newResults && newResults.innerHTML.trim() !== "") {
                    resultsContent.innerHTML = newResults.innerHTML;
                    resultsContent.style.display = "block";
                } else {
                    resultsContent.innerHTML = "<p style='text-align:center; padding:20px;'>No products found.</p>";
                }
                resultsContent.style.opacity = "1";
            })
            .catch(err => {
                console.error("Live Search Error:", err);
                resultsContent.innerHTML = "<p>Error connecting to server.</p>";
                resultsContent.style.opacity = "1";
            });
    }, 300);
});

// Stop the form from doing a full page reload if the user hits Enter
const searchForm = document.getElementById('searchForm');
if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
    });
}


    function openDeleteModal(deleteUrl) {
        // 1. Find the modal and the form inside it
        const modal = document.getElementById('deleteProductModal');
        const form = document.getElementById('deleteProductForm');
        
        // 2. Set the form action to the Django URL passed from the button
        form.action = deleteUrl;
        
        // 3. Show the modal (using 'flex' to center it)
        modal.style.display = 'flex';
    }

    function closeModal() {
        const modal = document.getElementById('deleteProductModal');
        modal.style.display = 'none';
    }

    // Optional: Close modal if user clicks outside the content box
    window.onclick = function(event) {
        const modal = document.getElementById('deleteProductModal');
        if (event.target == modal) {
            closeModal();
        }
    }
  

   function confirmDelete() {
        return confirm("Are you certain you want to delete this player?");
    }
