"""
Navi Travel Planning App - FastAPI Backend
Fixed to serve the frontend HTML and handle static files.
"""

import os
from datetime import date
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
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

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
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
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Warning: Supabase connection failed: {e}")

# Demo User ID (hardcoded for hackathon demo)
DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"

def get_demo_user() -> str:
    return DEMO_USER_ID

# --- DATA MODELS ---

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

class Attraction(BaseModel):
    id: str
    name: str
    destination: str
    category: str
    rating: float
    review_count: int
    price_point: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    scout_tip: Optional[str] = None
    is_local_favorite: bool = False
    lat: Optional[float] = None
    lng: Optional[float] = None
    views: int = 0

class SwipeCreate(BaseModel):
    trip_id: str
    attraction_id: str
    is_liked: bool = True

class Swipe(SwipeCreate):
    id: str
    user_id: str

class ItineraryItemBase(BaseModel):
    trip_id: str
    attraction_id: Optional[str] = None
    day_number: int
    start_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    order_index: int = 0
    notes: Optional[str] = None

class ItineraryItem(ItineraryItemBase):
    id: str

# --- API ENDPOINTS ---

@app.post("/trips", response_model=Trip)
def create_trip(trip: TripCreate, user_id: str = Depends(get_demo_user)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    try:
        trip_data = trip.model_dump(by_alias=True)
        # Convert dates to strings for JSON serialization
        trip_data["start_date"] = str(trip_data["start_date"])
        trip_data["end_date"] = str(trip_data["end_date"])
        trip_data["user_id"] = user_id
        
        response = supabase.table("trips").insert(trip_data).execute()
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create trip")
        return response.data[0]
    except Exception as e:
        print(f"Error creating trip: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/attractions", response_model=List[Attraction])
def get_attractions(
    destination: Optional[str] = Query(None),
    category: Optional[str] = Query(None)
):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    query = supabase.table("attractions").select("*")
    if destination:
        query = query.eq("destination", destination)
    if category:
        query = query.eq("category", category)
    
    response = query.order("rating", desc=True).execute()
    return response.data

@app.post("/swipes", response_model=Swipe)
def create_swipe(swipe: SwipeCreate, user_id: str = Depends(get_demo_user)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    swipe_data = swipe.model_dump()
    swipe_data["user_id"] = user_id
    
    # Use upsert to prevent duplicate swipes
    response = supabase.table("swipes").upsert(
        swipe_data, on_conflict="trip_id,attraction_id,user_id"
    ).execute()
    
    return response.data[0]

@app.get("/itinerary", response_model=List[ItineraryItem])
def get_itinerary(trip_id: str):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not configured")
    
    response = supabase.table("itinerary_items").select("*").eq("trip_id", trip_id).order("day_number").order("order_index").execute()
    return response.data

# --- FRONTEND SERVING (Must be last) ---

# 1. Fix the Favicon 404 error
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(content="", media_type="image/x-icon")

# 2. Serve static assets if you have them (images/css)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# 3. Serve the main HTML file at the root URL
@app.get("/")
async def read_index():
    return FileResponse("frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)