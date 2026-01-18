-- DANGER: This drops all existing tables to ensure a clean schema rebuild
DROP TABLE IF EXISTS trip_participants CASCADE;
DROP TABLE IF EXISTS swipes CASCADE;
DROP TABLE IF EXISTS itinerary_items CASCADE;
DROP TABLE IF EXISTS attractions CASCADE;
DROP TABLE IF EXISTS trips CASCADE;

-- NOW RECREATE EVERYTHING FRESH

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Trips table
CREATE TABLE trips (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    budget_limit DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    user_id UUID NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Attractions table
CREATE TABLE attractions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    destination VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    rating DECIMAL(3, 2) NOT NULL CHECK (rating >= 0 AND rating <= 5),
    review_count INTEGER NOT NULL DEFAULT 0,
    price_point VARCHAR(10),
    image_url TEXT,
    description TEXT,
    scout_tip TEXT,
    is_local_favorite BOOLEAN DEFAULT FALSE,
    lat DECIMAL(10, 8),
    lng DECIMAL(11, 8),
    views INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Itinerary Items table
CREATE TABLE itinerary_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    attraction_id UUID REFERENCES attractions(id) ON DELETE SET NULL,
    day_number INTEGER NOT NULL CHECK (day_number >= 1),
    start_time TIME,
    duration_minutes INTEGER,
    order_index INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(trip_id, day_number, order_index)
);

-- Swipes table
CREATE TABLE swipes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    attraction_id UUID NOT NULL REFERENCES attractions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL,
    is_liked BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(trip_id, attraction_id, user_id)
);

-- Trip Participants table
CREATE TABLE trip_participants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    trip_id UUID NOT NULL REFERENCES trips(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    avatar_url TEXT,
    user_id UUID,
    status VARCHAR(50) DEFAULT 'invited',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(trip_id, email)
);

-- Re-create indexes
CREATE INDEX idx_trips_user_id ON trips(user_id);
CREATE INDEX idx_trips_destination ON trips(destination);
CREATE INDEX idx_attractions_destination ON attractions(destination);
CREATE INDEX idx_attractions_category ON attractions(category);
CREATE INDEX idx_itinerary_items_trip_id ON itinerary_items(trip_id);
CREATE INDEX idx_itinerary_items_day ON itinerary_items(trip_id, day_number);
CREATE INDEX idx_swipes_trip_id ON swipes(trip_id);
CREATE INDEX idx_swipes_user_id ON swipes(user_id);
CREATE INDEX idx_trip_participants_trip_id ON trip_participants(trip_id);