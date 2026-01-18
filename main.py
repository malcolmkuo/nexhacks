"""
Navi Travel Planning App - FastAPI Backend
With Google Places API parallel fetching and website scraping
"""

import os
import asyncio
import json
import re
from datetime import date
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
import httpx
import googlemaps
import trafilatura

# Load environment variables
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

app = FastAPI(
    title="Navi Travel Planning API",
    description="Backend API with Google Places integration",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys
GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Initialize clients
supabase: Optional[Client] = None
gmaps: Optional[googlemaps.Client] = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase connected")
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")

if GOOGLE_MAPS_KEY:
    try:
        gmaps = googlemaps.Client(key=GOOGLE_MAPS_KEY)
        print("✅ Google Maps connected")
    except Exception as e:
        print(f"❌ Google Maps connection failed: {e}")

# Categories for parallel fetching
CATEGORIES = {
    "Food": ["restaurant", "cafe", "bakery", "bar"],
    "Sights": ["tourist_attraction", "museum", "art_gallery", "landmark"],
    "Nightlife": ["night_club", "bar", "casino"],
    "Shopping": ["shopping_mall", "store", "market"],
    "Hidden Gems": ["park", "spa", "temple", "shrine", "viewpoint"]
}

# ============================================================================
# DATA MODELS
# ============================================================================

class PlaceResult(BaseModel):
    id: Optional[str] = None
    google_place_id: str
    name: str
    city: str
    category: str
    location: Optional[Dict[str, float]] = None
    details: Dict[str, Any] = {}
    website_url: Optional[str] = None
    website_content: Dict[str, Any] = {}
    image_urls: List[str] = []
    is_local_favorite: bool = False

class SeedCityRequest(BaseModel):
    city: str

class SeedCityResponse(BaseModel):
    success: bool
    message: str
    places_added: int
    city: str

class TripCreate(BaseModel):
    name: str
    city: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget_limit: Optional[float] = 0

class SwipeCreate(BaseModel):
    trip_id: str
    place_id: str
    is_liked: bool = True

# ============================================================================
# GOOGLE PLACES API - PARALLEL FETCHING
# ============================================================================

async def fetch_places_by_category(city: str, category: str, place_types: List[str]) -> List[Dict]:
    """Fetch places for a single category using Google Places API"""
    if not gmaps:
        return []

    all_places = []
    seen_ids = set()

    for place_type in place_types:
        try:
            # Text search for this category in the city
            query = f"{place_type} in {city}"
            results = gmaps.places(query=query, type=place_type)

            for place in results.get("results", [])[:10]:  # Max 10 per type
                place_id = place.get("place_id")
                if place_id and place_id not in seen_ids:
                    seen_ids.add(place_id)

                    # Get photo URLs (reference only, not binary)
                    image_urls = []
                    for photo in place.get("photos", [])[:3]:
                        ref = photo.get("photo_reference")
                        if ref:
                            url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={ref}&key={GOOGLE_MAPS_KEY}"
                            image_urls.append(url)

                    all_places.append({
                        "google_place_id": place_id,
                        "name": place.get("name", ""),
                        "city": city,
                        "category": category,
                        "location": place.get("geometry", {}).get("location"),
                        "details": {
                            "rating": place.get("rating"),
                            "user_ratings_total": place.get("user_ratings_total", 0),
                            "price_level": place.get("price_level"),
                            "address": place.get("formatted_address", place.get("vicinity", "")),
                            "types": place.get("types", []),
                            "business_status": place.get("business_status"),
                        },
                        "image_urls": image_urls,
                        "is_local_favorite": (
                            place.get("rating", 0) >= 4.5 and
                            place.get("user_ratings_total", 0) >= 500
                        )
                    })
        except Exception as e:
            print(f"Error fetching {place_type} in {city}: {e}")
            continue

    return all_places


async def get_place_details(place_id: str) -> Dict:
    """Get detailed info for a place including website and photos"""
    if not gmaps:
        return {}

    try:
        details = gmaps.place(
            place_id=place_id,
            fields=["website", "formatted_phone_number", "opening_hours", "editorial_summary", "reviews", "photos"]
        )
        return details.get("result", {})
    except Exception as e:
        print(f"Error getting details for {place_id}: {e}")
        return {}


async def scrape_website(url: str) -> Dict[str, Any]:
    """Scrape website content using trafilatura, limit to 2kb"""
    if not url:
        return {}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, follow_redirects=True)
            if response.status_code != 200:
                return {}

            html = response.text

        # Extract text using trafilatura
        extracted = trafilatura.extract(html, include_comments=False, include_tables=False)

        if not extracted:
            return {}

        # Limit to 2kb
        text = extracted[:2048]

        # Extract keywords for menu/price/vibe
        text_lower = text.lower()

        # Common food/menu keywords
        menu_keywords = []
        food_terms = ["ramen", "sushi", "pizza", "burger", "steak", "pasta", "coffee", "tea",
                     "beer", "wine", "cocktail", "dessert", "breakfast", "lunch", "dinner",
                     "noodle", "rice", "soup", "salad", "seafood", "vegetarian", "vegan"]
        for term in food_terms:
            if term in text_lower:
                menu_keywords.append(term)

        # Price indicators
        price_range = None
        if "$$$" in text or "expensive" in text_lower or "fine dining" in text_lower:
            price_range = "$$$"
        elif "$$" in text or "moderate" in text_lower:
            price_range = "$$"
        elif "$" in text or "cheap" in text_lower or "budget" in text_lower:
            price_range = "$"

        # Vibe keywords
        vibe_keywords = []
        vibe_terms = ["cozy", "romantic", "lively", "quiet", "traditional", "modern",
                     "family", "casual", "upscale", "trendy", "authentic", "hidden gem",
                     "local favorite", "busy", "peaceful", "scenic", "rooftop"]
        for term in vibe_terms:
            if term in text_lower:
                vibe_keywords.append(term)

        return {
            "summary": text[:500],  # Short summary
            "menu_keywords": menu_keywords[:10],
            "price_range": price_range,
            "vibe_keywords": vibe_keywords[:10],
        }

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return {}


async def seed_city(city: str) -> int:
    """
    Main function to seed a city with places from Google Places API
    Uses parallel fetching for speed
    """
    if not gmaps or not supabase:
        raise HTTPException(status_code=500, detail="APIs not configured")

    print(f"🌍 Starting to seed {city}...")

    # STEP 1: Parallel fetch all categories
    tasks = []
    for category, place_types in CATEGORIES.items():
        tasks.append(fetch_places_by_category(city, category, place_types))

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Flatten and deduplicate
    all_places = []
    seen_ids = set()

    for result in results:
        if isinstance(result, Exception):
            print(f"Category fetch error: {result}")
            continue
        for place in result:
            pid = place["google_place_id"]
            if pid not in seen_ids:
                seen_ids.add(pid)
                all_places.append(place)

    print(f"📍 Found {len(all_places)} unique places")

    # STEP 2: Get detailed info for top 20 places (by rating)
    top_places = sorted(
        all_places,
        key=lambda x: (x["details"].get("rating") or 0) * (x["details"].get("user_ratings_total") or 0),
        reverse=True
    )[:20]

    # Fetch details in parallel
    detail_tasks = [get_place_details(p["google_place_id"]) for p in top_places]
    details_results = await asyncio.gather(*detail_tasks, return_exceptions=True)

    # Update places with details
    for i, details in enumerate(details_results):
        if isinstance(details, Exception) or not details:
            continue
        top_places[i]["website_url"] = details.get("website")
        if "opening_hours" in details:
            top_places[i]["details"]["opening_hours"] = details["opening_hours"].get("weekday_text", [])
        if "editorial_summary" in details:
            top_places[i]["details"]["editorial_summary"] = details["editorial_summary"].get("overview")
        if "reviews" in details:
            top_places[i]["details"]["reviews"] = [
                {"text": r.get("text", "")[:200], "rating": r.get("rating")}
                for r in details["reviews"][:3]
            ]
        # Get more photos from place details (up to 10 total)
        if "photos" in details:
            existing_urls = set(top_places[i].get("image_urls", []))
            for photo in details["photos"][:10]:
                ref = photo.get("photo_reference")
                if ref:
                    url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={ref}&key={GOOGLE_MAPS_KEY}"
                    if url not in existing_urls:
                        top_places[i]["image_urls"].append(url)
                        existing_urls.add(url)
                        if len(top_places[i]["image_urls"]) >= 10:
                            break

    # STEP 3: Scrape websites for top places (parallel)
    print("🌐 Scraping websites for top places...")
    websites = [p.get("website_url") for p in top_places]
    scrape_tasks = [scrape_website(url) for url in websites]
    scrape_results = await asyncio.gather(*scrape_tasks, return_exceptions=True)

    for i, scraped in enumerate(scrape_results):
        if isinstance(scraped, Exception) or not scraped:
            continue
        top_places[i]["website_content"] = scraped

    # Merge top_places back into all_places
    top_ids = {p["google_place_id"] for p in top_places}
    other_places = [p for p in all_places if p["google_place_id"] not in top_ids]
    final_places = top_places + other_places

    # STEP 4: Batch insert into Supabase
    print(f"💾 Saving {len(final_places)} places to database...")

    # Prepare data for insertion
    insert_data = []
    for place in final_places:
        loc = place.get("location")
        insert_data.append({
            "google_place_id": place["google_place_id"],
            "name": place["name"],
            "city": place["city"],
            "category": place["category"],
            "details": json.dumps(place.get("details", {})),
            "website_url": place.get("website_url"),
            "website_content": json.dumps(place.get("website_content", {})),
            "image_urls": place.get("image_urls", []),
            "is_local_favorite": place.get("is_local_favorite", False),
        })

    # Batch insert (upsert to handle duplicates)
    try:
        response = supabase.table("places").upsert(
            insert_data,
            on_conflict="google_place_id"
        ).execute()
        print(f"✅ Successfully saved {len(response.data)} places")
        return len(response.data)
    except Exception as e:
        print(f"❌ Database error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.post("/api/seed-city", response_model=SeedCityResponse)
async def api_seed_city(request: SeedCityRequest, background_tasks: BackgroundTasks):
    """
    Seed a city with places from Google Places API.
    Fetches ~100 places across 5 categories in parallel.
    """
    city = request.city
    places_added = await seed_city(city)

    return SeedCityResponse(
        success=True,
        message=f"Successfully seeded {city} with {places_added} places",
        places_added=places_added,
        city=city
    )


@app.get("/api/places")
async def get_places(
    city: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """Get places from database, optionally filtered by city and category"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")

    query = supabase.table("places").select("*")

    if city:
        query = query.eq("city", city)
    if category:
        query = query.eq("category", category)

    response = query.limit(limit).execute()

    # Parse JSONB fields
    places = []
    for row in response.data:
        row["details"] = json.loads(row["details"]) if isinstance(row["details"], str) else row["details"]
        row["website_content"] = json.loads(row["website_content"]) if isinstance(row["website_content"], str) else row["website_content"]
        places.append(row)

    return places


@app.get("/api/places/{place_id}")
async def get_place(place_id: str):
    """Get a single place by ID"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")

    response = supabase.table("places").select("*").eq("id", place_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Place not found")

    place = response.data
    place["details"] = json.loads(place["details"]) if isinstance(place["details"], str) else place["details"]
    place["website_content"] = json.loads(place["website_content"]) if isinstance(place["website_content"], str) else place["website_content"]

    return place


@app.post("/api/trips")
async def create_trip(trip: TripCreate):
    """Create a new trip"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")

    trip_data = {
        "name": trip.name,
        "city": trip.city,
        "start_date": trip.start_date,
        "end_date": trip.end_date,
        "budget_limit": trip.budget_limit or 0,
        "user_id": "demo_user"
    }

    response = supabase.table("trips").insert(trip_data).execute()
    return response.data[0]


@app.get("/api/trips/{trip_id}")
async def get_trip(trip_id: str):
    """Get a trip by ID"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")

    response = supabase.table("trips").select("*").eq("id", trip_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Trip not found")
    return response.data


@app.post("/api/swipes")
async def create_swipe(swipe: SwipeCreate):
    """Record a swipe on a place"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")

    swipe_data = {
        "trip_id": swipe.trip_id,
        "place_id": swipe.place_id,
        "is_liked": swipe.is_liked,
        "user_id": "demo_user"
    }

    response = supabase.table("swipes").upsert(
        swipe_data,
        on_conflict="trip_id,place_id,user_id"
    ).execute()

    return response.data[0]


@app.get("/api/trips/{trip_id}/liked-places")
async def get_liked_places(trip_id: str):
    """Get all liked places for a trip"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Get liked swipes
    swipes = supabase.table("swipes").select("place_id").eq("trip_id", trip_id).eq("is_liked", True).execute()
    place_ids = [s["place_id"] for s in swipes.data]

    if not place_ids:
        return []

    # Get place details
    places = supabase.table("places").select("*").in_("id", place_ids).execute()
    return places.data


# ============================================================================
# IMAGE PROXY (to avoid CORS issues with Google Photos)
# ============================================================================

@app.get("/api/image-proxy")
async def image_proxy(url: str = Query(...)):
    """Proxy Google Places photos to avoid CORS issues"""
    if not url.startswith("https://maps.googleapis.com"):
        raise HTTPException(status_code=400, detail="Invalid URL")

    async with httpx.AsyncClient() as client:
        response = await client.get(url, follow_redirects=True)
        return Response(
            content=response.content,
            media_type=response.headers.get("content-type", "image/jpeg")
        )


# ============================================================================
# HEALTH & FRONTEND
# ============================================================================

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "google_maps": bool(GOOGLE_MAPS_KEY),
        "supabase": bool(supabase)
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content="", media_type="image/x-icon")


# Serve frontend static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")


@app.get("/")
async def read_index():
    return FileResponse("frontend/activity_swipe_deck/code.html")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
