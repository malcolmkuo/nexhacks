/**
 * Navi Travel App - Frontend JavaScript
 * Connects swipe deck to backend API with real Google Places data
 */

const API_BASE = 'http://localhost:8000';

// State
let places = [];
let currentIndex = 0;
let likedPlaces = [];
let currentTrip = null;
let currentCategory = 'All';

// ============================================================================
// INITIALIZATION
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    console.log('🚀 Navi App Initialized');

    // Create or get trip
    await initTrip();

    // Load places
    await loadPlaces();

    // Setup event listeners
    setupSwipeButtons();
    setupCategoryFilters();
    setupKeyboardControls();
});

async function initTrip() {
    // Check localStorage for existing trip
    const tripId = localStorage.getItem('navi_trip_id');

    if (tripId) {
        try {
            const response = await fetch(`${API_BASE}/api/trips/${tripId}`);
            if (response.ok) {
                currentTrip = await response.json();
                console.log('📍 Loaded existing trip:', currentTrip);
                return;
            }
        } catch (e) {
            console.log('Creating new trip...');
        }
    }

    // Create new trip
    try {
        const response = await fetch(`${API_BASE}/api/trips`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: 'Tokyo Adventure',
                city: 'Tokyo',
                start_date: new Date().toISOString().split('T')[0],
                end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                budget_limit: 2000
            })
        });
        currentTrip = await response.json();
        localStorage.setItem('navi_trip_id', currentTrip.id);
        console.log('✅ Created new trip:', currentTrip);
    } catch (e) {
        console.error('Failed to create trip:', e);
    }
}

// ============================================================================
// PLACES LOADING
// ============================================================================

async function loadPlaces(category = 'All') {
    try {
        let url = `${API_BASE}/api/places?city=Tokyo&limit=50`;
        if (category && category !== 'All') {
            url += `&category=${encodeURIComponent(category)}`;
        }

        const response = await fetch(url);
        places = await response.json();
        currentIndex = 0;

        console.log(`📍 Loaded ${places.length} places for ${category}`);

        updateProgress();
        renderCurrentCard();
    } catch (e) {
        console.error('Failed to load places:', e);
    }
}

// ============================================================================
// CARD RENDERING
// ============================================================================

function getProxiedImageUrl(url) {
    if (!url) return 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800';
    if (url.includes('maps.googleapis.com')) {
        return `${API_BASE}/api/image-proxy?url=${encodeURIComponent(url)}`;
    }
    return url;
}

function renderCurrentCard() {
    if (currentIndex >= places.length) {
        showCompletionState();
        return;
    }

    const place = places[currentIndex];
    const card = document.querySelector('#swipe-card');
    if (!card) return;

    // Get image URL - use first image or fallback (through proxy)
    const rawImageUrl = place.image_urls && place.image_urls.length > 0
        ? place.image_urls[0]
        : null;
    const imageUrl = getProxiedImageUrl(rawImageUrl);

    // Update background image
    const bgDiv = document.getElementById('card-bg');
    if (bgDiv) {
        bgDiv.style.backgroundImage = `url("${imageUrl}")`;
    }

    // Update title using ID
    const title = document.getElementById('place-name');
    if (title) {
        title.textContent = place.name;
    }

    // Update details (rating, price, category)
    const details = place.details || {};
    const rating = details.rating || 4.5;
    const reviewCount = details.user_ratings_total || 0;
    const priceLevel = details.price_level;
    const priceText = priceLevel ? '$'.repeat(priceLevel) : '$$';

    // Update price using ID
    const priceSpan = document.getElementById('price-text');
    if (priceSpan) {
        priceSpan.textContent = priceText;
    }

    // Update category using ID
    const categorySpan = document.getElementById('category-text');
    if (categorySpan) {
        categorySpan.textContent = place.category;
    }

    // Update rating using ID
    const ratingSpan = document.getElementById('rating-text');
    if (ratingSpan) {
        ratingSpan.textContent = rating.toFixed(1);
    }

    // Update reviews using ID
    const reviewSpan = document.getElementById('reviews-text');
    if (reviewSpan) {
        reviewSpan.textContent = `(${formatNumber(reviewCount)})`;
    }

    // Update type badge based on category
    const typeBadge = document.getElementById('type-badge');
    const typeText = document.getElementById('type-text');
    if (typeBadge && typeText) {
        const categoryIcons = {
            'Food': 'restaurant',
            'Sights': 'photo_camera',
            'Nightlife': 'nightlife',
            'Shopping': 'shopping_bag',
            'Hidden Gems': 'diamond'
        };
        const icon = categoryIcons[place.category] || 'place';
        typeBadge.querySelector('.material-symbols-outlined').textContent = icon;
        typeText.textContent = place.category;
    }

    // Update local favorite badge
    const favoriteBadge = document.getElementById('local-favorite-badge');
    if (favoriteBadge) {
        favoriteBadge.style.display = place.is_local_favorite ? 'flex' : 'none';
    }

    // Store place data on card for hover/details
    card.dataset.placeId = place.id;
    card.dataset.allImages = JSON.stringify(place.image_urls || []);
    card.dataset.openingHours = JSON.stringify(details.opening_hours || []);

    // Setup hover for more images
    setupImageHover(card, place.image_urls || []);
}

// Store hover state globally to prevent duplicate listeners
let hoverInterval = null;
let currentHoverImages = [];

function setupImageHover(card, images) {
    // Remove existing dots
    const existingDots = card.querySelector('.image-dots');
    if (existingDots) {
        existingDots.remove();
    }

    // Clear any existing interval
    if (hoverInterval) {
        clearInterval(hoverInterval);
        hoverInterval = null;
    }

    if (images.length <= 1) return;

    // Proxy all images
    currentHoverImages = images.map(url => getProxiedImageUrl(url));

    const bgDiv = document.getElementById('card-bg');
    if (!bgDiv) return;

    // Create image indicator dots
    const dotsContainer = document.createElement('div');
    dotsContainer.className = 'image-dots absolute top-4 left-1/2 -translate-x-1/2 flex gap-1 z-30';
    dotsContainer.innerHTML = currentHoverImages.slice(0, 5).map((_, i) =>
        `<div class="w-2 h-2 rounded-full ${i === 0 ? 'bg-white' : 'bg-white/40'} transition-all"></div>`
    ).join('');
    card.appendChild(dotsContainer);

    // Only setup listeners once per card
    if (!card.dataset.hoverSetup) {
        card.dataset.hoverSetup = 'true';
        let currentImageIndex = 0;

        card.addEventListener('mouseenter', () => {
            if (currentHoverImages.length <= 1) return;
            currentImageIndex = 0;

            hoverInterval = setInterval(() => {
                currentImageIndex = (currentImageIndex + 1) % Math.min(currentHoverImages.length, 5);
                bgDiv.style.backgroundImage = `url("${currentHoverImages[currentImageIndex]}")`;

                // Update dots
                const dots = card.querySelector('.image-dots');
                if (dots) {
                    dots.querySelectorAll('div').forEach((dot, i) => {
                        dot.className = `w-2 h-2 rounded-full ${i === currentImageIndex ? 'bg-white' : 'bg-white/40'} transition-all`;
                    });
                }
            }, 1500);
        });

        card.addEventListener('mouseleave', () => {
            if (hoverInterval) {
                clearInterval(hoverInterval);
                hoverInterval = null;
            }
            currentImageIndex = 0;
            if (currentHoverImages.length > 0) {
                bgDiv.style.backgroundImage = `url("${currentHoverImages[0]}")`;
            }

            const dots = card.querySelector('.image-dots');
            if (dots) {
                dots.querySelectorAll('div').forEach((dot, i) => {
                    dot.className = `w-2 h-2 rounded-full ${i === 0 ? 'bg-white' : 'bg-white/40'} transition-all`;
                });
            }
        });
    }
}

// ============================================================================
// SWIPE ACTIONS
// ============================================================================

function setupSwipeButtons() {
    // Pass button (X) - using ID selector
    const passBtn = document.getElementById('pass-btn');
    if (passBtn) {
        passBtn.addEventListener('click', () => handleSwipe(false));
    }

    // Like button (Heart) - using ID selector
    const likeBtn = document.getElementById('like-btn');
    if (likeBtn) {
        likeBtn.addEventListener('click', () => handleSwipe(true));
    }
}

function setupKeyboardControls() {
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            handleSwipe(false);
        } else if (e.key === 'ArrowRight') {
            handleSwipe(true);
        }
    });
}

async function handleSwipe(isLiked) {
    if (currentIndex >= places.length) return;

    const place = places[currentIndex];

    // Animate card
    const card = document.querySelector('#swipe-card');
    if (card) {
        card.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
        card.style.transform = isLiked ? 'translateX(100px) rotate(10deg)' : 'translateX(-100px) rotate(-10deg)';
        card.style.opacity = '0';
    }

    // Record swipe to backend
    if (currentTrip) {
        try {
            await fetch(`${API_BASE}/api/swipes`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    trip_id: currentTrip.id,
                    place_id: place.id,
                    is_liked: isLiked
                })
            });

            if (isLiked) {
                likedPlaces.push(place);
                console.log(`❤️ Liked: ${place.name}`);

                // Auto-add to itinerary
                await addToItinerary(place);
            }
        } catch (e) {
            console.error('Failed to record swipe:', e);
        }
    }

    // Move to next card
    setTimeout(() => {
        currentIndex++;
        updateProgress();

        if (card) {
            card.style.transition = 'none';
            card.style.transform = '';
            card.style.opacity = '1';
        }

        renderCurrentCard();
    }, 300);
}

async function addToItinerary(place) {
    // Automatically add liked places to itinerary
    // Assign to day based on how many we have
    const dayNumber = Math.floor(likedPlaces.length / 4) + 1;
    const timeSlots = ['09:00', '12:00', '15:00', '19:00'];
    const slotIndex = (likedPlaces.length - 1) % 4;

    try {
        // Note: Would need to add this endpoint to backend
        // For now, just store locally
        console.log(`📅 Added to Day ${dayNumber} at ${timeSlots[slotIndex]}: ${place.name}`);
    } catch (e) {
        console.error('Failed to add to itinerary:', e);
    }
}

// ============================================================================
// CATEGORY FILTERS
// ============================================================================

function setupCategoryFilters() {
    const buttons = document.querySelectorAll('header button[data-category]');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            buttons.forEach(b => {
                b.classList.remove('bg-secondary', 'text-white', 'shadow-md');
                b.classList.add('bg-white', 'text-secondary', 'border', 'border-[#ebdcd5]');
            });

            btn.classList.remove('bg-white', 'text-secondary', 'border', 'border-[#ebdcd5]');
            btn.classList.add('bg-secondary', 'text-white', 'shadow-md');

            // Get category from data attribute
            const category = btn.dataset.category || 'All';
            currentCategory = category;

            loadPlaces(category);
        });
    });
}

// ============================================================================
// UI HELPERS
// ============================================================================

function updateProgress() {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');

    if (progressBar) {
        const percent = places.length > 0 ? (currentIndex / places.length) * 100 : 0;
        progressBar.style.width = `${percent}%`;
    }

    if (progressText) {
        progressText.innerHTML = `${currentIndex}<span class="text-gray-400 dark:text-gray-500 font-medium">/${places.length}</span>`;
    }
}

function showCompletionState() {
    const card = document.querySelector('#swipe-card');
    if (!card) return;

    card.innerHTML = `
        <div class="absolute inset-0 bg-gradient-to-br from-indigo-600 to-purple-700 flex flex-col items-center justify-center p-8 text-white text-center">
            <span class="material-symbols-outlined text-6xl mb-4">celebration</span>
            <h2 class="text-2xl font-bold mb-2">All Done!</h2>
            <p class="text-white/80 mb-6">You've swiped through all ${places.length} places</p>
            <p class="text-lg font-semibold">❤️ ${likedPlaces.length} places liked</p>
            <button onclick="window.location.href='../final_group_itinerary/code.html'"
                    class="mt-6 px-6 py-3 bg-white text-indigo-600 font-bold rounded-xl hover:bg-white/90 transition-all">
                View Itinerary →
            </button>
        </div>
    `;
}

function formatNumber(num) {
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
}

// ============================================================================
// OPENING HOURS CHECK
// ============================================================================

function isOpenAt(openingHours, checkTime) {
    // Parse opening hours and check if place is open
    // Format: ["Monday: 9:00 AM – 10:00 PM", ...]
    if (!openingHours || openingHours.length === 0) return true; // Assume open if no data

    const days = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const today = new Date();
    const dayName = days[today.getDay()];

    const todayHours = openingHours.find(h => h.startsWith(dayName));
    if (!todayHours) return true;

    if (todayHours.includes('Closed')) return false;
    if (todayHours.includes('Open 24 hours')) return true;

    // Parse time range if checkTime is provided
    if (checkTime) {
        // Extract hours from string like "Monday: 9:00 AM – 10:00 PM"
        const timeMatch = todayHours.match(/(\d{1,2}):(\d{2})\s*(AM|PM)\s*[–-]\s*(\d{1,2}):(\d{2})\s*(AM|PM)/i);
        if (timeMatch) {
            const [, openH, openM, openPeriod, closeH, closeM, closePeriod] = timeMatch;
            let openHour = parseInt(openH) + (openPeriod.toUpperCase() === 'PM' && openH !== '12' ? 12 : 0);
            let closeHour = parseInt(closeH) + (closePeriod.toUpperCase() === 'PM' && closeH !== '12' ? 12 : 0);
            if (openPeriod.toUpperCase() === 'AM' && openH === '12') openHour = 0;
            if (closePeriod.toUpperCase() === 'AM' && closeH === '12') closeHour = 0;

            const [checkH, checkM] = checkTime.split(':').map(Number);
            const checkMinutes = checkH * 60 + checkM;
            const openMinutes = openHour * 60 + parseInt(openM);
            const closeMinutes = closeHour * 60 + parseInt(closeM);

            return checkMinutes >= openMinutes && checkMinutes <= closeMinutes;
        }
    }

    return true;
}

function getOpeningWarning(place, proposedTime) {
    const hours = place.details?.opening_hours || [];
    if (!isOpenAt(hours, proposedTime)) {
        return `⚠️ ${place.name} may be closed at ${proposedTime}`;
    }
    return null;
}
