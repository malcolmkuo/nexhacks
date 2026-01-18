-- Navi Travel App Database Schema
-- Run this in Supabase SQL Editor

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- DANGER: Drop existing tables for clean rebuild
DROP TABLE IF EXISTS swipes CASCADE;
DROP TABLE IF EXISTS itinerary_items CASCADE;
DROP TABLE IF EXISTS trips CASCADE;
DROP TABLE IF EXISTS places CASCADE;

-- ============================================================================
-- PLACES TABLE - Core table for Google Places data
-- ============================================================================
CREATE TABLE places (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    google_place_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    category TEXT NOT NULL, -- Food, Sights, Nightlife, Shopping, Hidden Gems

    -- Geographic location
    location GEOGRAPHY(POINT, 4326),

    -- Core details from Google Places API (JSONB for flexibility)
    details JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "rating": 4.5,
    --   "user_ratings_total": 1234,
    --   "price_level": 2,
    --   "address": "123 Main St, Tokyo",
    --   "phone": "+81-3-1234-5678",
    --   "opening_hours": ["Mon: 9AM-10PM", ...],
    --   "types": ["restaurant", "food"],
    --   "editorial_summary": "A great place..."
    -- }

    -- Website URL
    website_url TEXT,

    -- Scraped website content (max 2kb per site)
    website_content JSONB DEFAULT '{}'::jsonb,
    -- Structure: {
    --   "menu_keywords": ["ramen", "gyoza"],
    --   "price_range": "$10-30",
    --   "vibe_keywords": ["cozy", "traditional"],
    --   "summary": "Scraped text..."
    -- }

    -- Image URLs only - NO binary data (saves storage)
    image_urls TEXT[] DEFAULT ARRAY[]::TEXT[],

    -- Flags
    is_local_favorite BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- TRIPS TABLE
-- ============================================================================
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL DEFAULT 'demo_user',
    name TEXT NOT NULL,
    city TEXT NOT NULL,
    start_date DATE,
    end_date DATE,
    budget_limit DECIMAL(10, 2) DEFAULT 0.00,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- SWIPES TABLE
-- ============================================================================
CREATE TABLE swipes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
    place_id UUID REFERENCES places(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL DEFAULT 'demo_user',
    is_liked BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(trip_id, place_id, user_id)
);

-- ============================================================================
-- ITINERARY_ITEMS TABLE
-- ============================================================================
CREATE TABLE itinerary_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID REFERENCES trips(id) ON DELETE CASCADE,
    place_id UUID REFERENCES places(id) ON DELETE SET NULL,
    day_number INTEGER NOT NULL,
    time_slot TEXT,
    duration_minutes INTEGER DEFAULT 60,
    order_index INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- INDEXES for fast queries
-- ============================================================================
CREATE INDEX idx_places_city ON places(city);
CREATE INDEX idx_places_category ON places(category);
CREATE INDEX idx_places_city_category ON places(city, category);
CREATE INDEX idx_places_google_id ON places(google_place_id);
CREATE INDEX idx_trips_user ON trips(user_id);
CREATE INDEX idx_trips_city ON trips(city);
CREATE INDEX idx_swipes_trip ON swipes(trip_id);
CREATE INDEX idx_itinerary_trip ON itinerary_items(trip_id);

-- ============================================================================
-- AUTO-UPDATE updated_at
-- ============================================================================
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER places_updated_at
    BEFORE UPDATE ON places FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trips_updated_at
    BEFORE UPDATE ON trips FOR EACH ROW EXECUTE FUNCTION update_updated_at();
