"""
Navi Travel Planning App - FastAPI Backend
Completely rewritten to match frontend requirements
"""

import os
from datetime import date, time
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Navi Travel Planning API",
    description="Backend API for Navi group travel planning application",
    version="2.0.0"
)

# CORS Configuration - Allow localhost:3000 (or * for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],  # Allow all origins for hackathon demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Initialize Supabase client
supabase: Optional[Client] = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Demo User ID (hardcoded for hackathon demo)
DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"

# Auth Bypass Dependency - Automatically injects Demo User ID
def get_demo_user() -> str:
    """
    Auth bypass for hackathon demo.
    Automatically returns Demo User ID for all requests.
    Does NOT require Bearer token.
    """
    return DEMO_USER_ID

# Pydantic Models

class TripBase(BaseModel):
    name: str
    destination: str
    start_date: date
    end_date: date
    budget_limit: float = Field(..., alias="budget_limit")

class TripCreate(TripBase):
    pass

class Trip(TripBase):
    id: str
    user_id: str
    created_at: str
    updated_at: str

    class Config:
        populate_by_name = True
        from_attributes = True

class AttractionBase(BaseModel):
    name: str
    destination: str
    category: str
    rating: float = Field(..., ge=0.0, le=5.0)
    review_count: int = Field(..., ge=0)
    price_point: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    scout_tip: Optional[str] = None
    is_local_favorite: bool = False
    lat: Optional[float] = None
    lng: Optional[float] = None

class Attraction(AttractionBase):
    id: str
    views: int = 0
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

class SwipeCreate(BaseModel):
    trip_id: str
    attraction_id: str
    is_liked: bool = True  # true = right swipe/like, false = left swipe/pass

class Swipe(SwipeCreate):
    id: str
    user_id: str
    created_at: str

    class Config:
        from_attributes = True

class ItineraryItemBase(BaseModel):
    trip_id: str
    attraction_id: Optional[str] = None
    day_number: int = Field(..., ge=1)
    start_time: Optional[str] = None  # Time as string "HH:MM"
    duration_minutes: Optional[int] = None
    order_index: int = 0
    notes: Optional[str] = None

class ItineraryItem(ItineraryItemBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

# API Endpoints

@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "Navi Travel Planning API",
        "version": "2.0.0",
        "status": "operational",
        "demo_user_id": DEMO_USER_ID
    }

@app.get("/trips", response_model=List[Trip])
def get_trips(user_id: str = Depends(get_demo_user)):
    """
    GET /trips
    Fetch all trips for the demo user
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        response = supabase.table("trips").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trips: {str(e)}")

@app.post("/trips", response_model=Trip)
def create_trip(trip: TripCreate, user_id: str = Depends(get_demo_user)):
    """
    POST /trips
    Create a new trip
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        trip_data = trip.model_dump(by_alias=True)
        trip_data["user_id"] = user_id
        response = supabase.table("trips").insert(trip_data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create trip")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating trip: {str(e)}")

@app.get("/trips/{trip_id}", response_model=Trip)
def get_trip(trip_id: str, user_id: str = Depends(get_demo_user)):
    """
    GET /trips/{trip_id}
    Get a specific trip by ID
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        response = supabase.table("trips").select("*").eq("id", trip_id).eq("user_id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Trip not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trip: {str(e)}")

@app.get("/attractions", response_model=List[Attraction])
def get_attractions(
    destination: Optional[str] = Query(None, description="Filter by destination (e.g., 'Tokyo')"),
    category: Optional[str] = Query(None, description="Filter by category (Food & Drink, Adventure, Relaxation, Observation)"),
    limit: int = Query(100, ge=1, le=500)
):
    """
    GET /attractions
    Fetch attractions for the swipe deck
    Optionally filtered by destination and category
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        query = supabase.table("attractions").select("*")
        
        if destination:
            query = query.eq("destination", destination)
        if category:
            query = query.eq("category", category)
        
        query = query.limit(limit).order("rating", desc=True)
        response = query.execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attractions: {str(e)}")

@app.get("/attractions/{attraction_id}", response_model=Attraction)
def get_attraction(attraction_id: str):
    """
    GET /attractions/{attraction_id}
    Get a specific attraction by ID
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        response = supabase.table("attractions").select("*").eq("id", attraction_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Attraction not found")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching attraction: {str(e)}")

@app.post("/swipes", response_model=Swipe)
def create_swipe(swipe: SwipeCreate, user_id: str = Depends(get_demo_user)):
    """
    POST /swipes
    Save a right-swipe (like) or left-swipe (pass) for an attraction
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        # Verify trip belongs to user
        trip_check = supabase.table("trips").select("id").eq("id", swipe.trip_id).eq("user_id", user_id).execute()
        if not trip_check.data:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        swipe_data = swipe.model_dump()
        swipe_data["user_id"] = user_id
        
        # Use upsert to handle duplicate swipes (update if exists, insert if not)
        response = supabase.table("swipes").upsert(
            swipe_data,
            on_conflict="trip_id,attraction_id,user_id"
        ).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to save swipe")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving swipe: {str(e)}")

@app.get("/swipes", response_model=List[Swipe])
def get_swipes(
    trip_id: str = Query(..., description="Trip ID"),
    user_id: str = Depends(get_demo_user)
):
    """
    GET /swipes?trip_id={trip_id}
    Get all swipes (likes) for a trip
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        response = supabase.table("swipes").select("*").eq("trip_id", trip_id).eq("user_id", user_id).eq("is_liked", True).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching swipes: {str(e)}")

@app.get("/itinerary", response_model=List[ItineraryItem])
def get_itinerary(
    trip_id: str = Query(..., description="Trip ID"),
    day: Optional[int] = Query(None, description="Filter by day number (Day 1, Day 2, etc.)"),
    user_id: str = Depends(get_demo_user)
):
    """
    GET /itinerary?trip_id={trip_id}&day={day}
    Fetch itinerary items for a trip (final plan)
    Optionally filtered by day number for multi-day tabs
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        # Verify trip belongs to user
        trip_check = supabase.table("trips").select("id").eq("id", trip_id).eq("user_id", user_id).execute()
        if not trip_check.data:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        query = supabase.table("itinerary_items").select("*").eq("trip_id", trip_id)
        
        if day:
            query = query.eq("day_number", day)
        
        query = query.order("day_number").order("order_index")
        response = query.execute()
        return response.data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching itinerary: {str(e)}")

@app.post("/itinerary", response_model=ItineraryItem)
def create_itinerary_item(item: ItineraryItemBase, user_id: str = Depends(get_demo_user)):
    """
    POST /itinerary
    Add an item to the itinerary
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        # Verify trip belongs to user
        trip_check = supabase.table("trips").select("id").eq("id", item.trip_id).eq("user_id", user_id).execute()
        if not trip_check.data:
            raise HTTPException(status_code=404, detail="Trip not found")
        
        item_data = item.model_dump()
        response = supabase.table("itinerary_items").insert(item_data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create itinerary item")
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating itinerary item: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
