"""
Navi Travel Planning App - Seed Data Script
Completely rewritten with rich mock data for Tokyo attractions
"""

import os
from datetime import date, timedelta
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_KEY must be set in .env file")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Demo User ID
DEMO_USER_ID = "00000000-0000-0000-0000-000000000001"

# Rich Mock Data for Tokyo Attractions with Unsplash Images
TOKYO_ATTRACTIONS = [
    {
        "name": "Shibuya Sky Deck",
        "destination": "Tokyo",
        "category": "Observation",
        "rating": 4.8,
        "review_count": 2140,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800&q=80",
        "description": "Stunning 360-degree views of Tokyo from the rooftop observation deck. Perfect for sunset and night photography.",
        "scout_tip": "Best sunset view is at 5pm. Book tickets in advance to avoid long queues.",
        "is_local_favorite": True,
        "lat": 35.6586,
        "lng": 139.7034
    },
    {
        "name": "Tsukiji Outer Market",
        "destination": "Tokyo",
        "category": "Food & Drink",
        "rating": 4.7,
        "review_count": 8500,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1559339352-11d035aa65de?w=800&q=80",
        "description": "Famous fish market with incredible fresh sushi, street food, and traditional Japanese breakfast options.",
        "scout_tip": "Arrive early (before 9 AM) for the freshest seafood. Most stalls only accept cash.",
        "is_local_favorite": True,
        "lat": 35.6654,
        "lng": 139.7699
    },
    {
        "name": "Senso-ji Temple",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.6,
        "review_count": 32000,
        "price_point": "Free",
        "image_url": "https://images.unsplash.com/photo-1545569341-9eb8b30979d9?w=800&q=80",
        "description": "Tokyo's oldest temple with a vibrant shopping street leading to the main hall. A must-see cultural experience.",
        "scout_tip": "Visit early morning or late evening to avoid crowds. The temple is beautifully lit at night.",
        "is_local_favorite": False,
        "lat": 35.7148,
        "lng": 139.7967
    },
    {
        "name": "TeamLab Borderless",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.9,
        "review_count": 15200,
        "price_point": "$$$",
        "image_url": "https://images.unsplash.com/photo-1567427017947-545c5f8d16ad?w=800&q=80",
        "description": "Immersive digital art museum where boundaries dissolve between artwork and visitors. A truly unique experience.",
        "scout_tip": "Wear white or light-colored clothing to fully experience the interactive installations. Allow 2-3 hours.",
        "is_local_favorite": True,
        "lat": 35.6262,
        "lng": 139.7764
    },
    {
        "name": "Afuri Ramen",
        "destination": "Tokyo",
        "category": "Food & Drink",
        "rating": 4.6,
        "review_count": 4250,
        "price_point": "$",
        "image_url": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&q=80",
        "description": "Famous for their Yuzu Shio Ramen. Light, refreshing, and perfectly balanced. A Tokyo favorite.",
        "scout_tip": "Order via the vending machine at the entrance. The yuzu ramen is their signature dish.",
        "is_local_favorite": False,
        "lat": 35.6580,
        "lng": 139.7016
    },
    {
        "name": "Tokyo Skytree",
        "destination": "Tokyo",
        "category": "Observation",
        "rating": 4.5,
        "review_count": 28000,
        "price_point": "$$$",
        "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80",
        "description": "World's tallest freestanding tower with panoramic views of Tokyo and beyond. Two observation decks available.",
        "scout_tip": "Book Fast Skytree tickets online to skip the queue. Weather can affect visibility, check forecast.",
        "is_local_favorite": False,
        "lat": 35.7101,
        "lng": 139.8107
    },
    {
        "name": "Meiji Shrine",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.7,
        "review_count": 18200,
        "price_point": "Free",
        "image_url": "https://images.unsplash.com/photo-1528164344705-47542687000d?w=800&q=80",
        "description": "Peaceful Shinto shrine surrounded by a lush forest in the heart of Tokyo. A serene escape from the city.",
        "scout_tip": "Early morning visits are most peaceful. You can write wishes on wooden plaques (ema) at the shrine.",
        "is_local_favorite": True,
        "lat": 35.6764,
        "lng": 139.6993
    },
    {
        "name": "Robot Restaurant",
        "destination": "Tokyo",
        "category": "Food & Drink",
        "rating": 4.4,
        "review_count": 12000,
        "price_point": "$$$",
        "image_url": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&q=80",
        "description": "Over-the-top entertainment venue with robots, dancers, and neon lights. A quintessential Tokyo experience.",
        "scout_tip": "This is more about the show than the food. Book tickets well in advance, especially for evening shows.",
        "is_local_favorite": False,
        "lat": 35.6938,
        "lng": 139.7034
    },
    {
        "name": "Golden Gai Shinjuku",
        "destination": "Tokyo",
        "category": "Food & Drink",
        "rating": 4.5,
        "review_count": 6800,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=800&q=80",
        "description": "Historic narrow alleys with tiny bars. Each bar has only a few seats, creating an intimate atmosphere.",
        "scout_tip": "Many bars have cover charges (¥500-1000). Some are regulars-only, look for English signs.",
        "is_local_favorite": True,
        "lat": 35.6938,
        "lng": 139.7034
    },
    {
        "name": "Ueno Park",
        "destination": "Tokyo",
        "category": "Relaxation",
        "rating": 4.6,
        "review_count": 22000,
        "price_point": "Free",
        "image_url": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&q=80",
        "description": "Large public park with museums, temples, and a zoo. Perfect for cherry blossoms in spring and autumn colors.",
        "scout_tip": "Best visited during cherry blossom season (late March to early April) or autumn (November).",
        "is_local_favorite": False,
        "lat": 35.7132,
        "lng": 139.7730
    },
    {
        "name": "Izakaya Yurakucho",
        "destination": "Tokyo",
        "category": "Food & Drink",
        "rating": 4.7,
        "review_count": 5300,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800&q=80",
        "description": "Traditional Japanese pub under the train tracks. Authentic atmosphere with delicious grilled skewers and sake.",
        "scout_tip": "Go during dinner hours for the full experience. Try the yakitori (grilled chicken skewers) and local sake.",
        "is_local_favorite": True,
        "lat": 35.6748,
        "lng": 139.7614
    },
    {
        "name": "Harajuku Takeshita Street",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.3,
        "review_count": 19000,
        "price_point": "$",
        "image_url": "https://images.unsplash.com/photo-1524222717473-730000096953?w=800&q=80",
        "description": "Famous shopping street known for youth culture, quirky fashion, and unique street food like crepes.",
        "scout_tip": "Weekends are extremely crowded. Visit on a weekday morning for a better experience. Try the rainbow cotton candy.",
        "is_local_favorite": False,
        "lat": 35.6702,
        "lng": 139.7026
    },
    {
        "name": "Tokyo National Museum",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.7,
        "review_count": 14000,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&q=80",
        "description": "Japan's oldest and largest art museum with an extensive collection of Japanese and Asian art.",
        "scout_tip": "The Honkan (Japanese Gallery) is a must-see. Allow at least 3 hours to properly explore.",
        "is_local_favorite": False,
        "lat": 35.7193,
        "lng": 139.7768
    },
    {
        "name": "Sukiyabashi Jiro (Dream)",
        "destination": "Tokyo",
        "category": "Food & Drink",
        "rating": 4.8,
        "review_count": 2400,
        "price_point": "$$$",
        "image_url": "https://images.unsplash.com/photo-1563612292-1bb64e6380ec?w=800&q=80",
        "description": "Legendary sushi experience (inspired by Jiro Dreams of Sushi). Omakase course featuring the freshest ingredients.",
        "scout_tip": "Reservations are extremely difficult. Book months in advance through your hotel concierge.",
        "is_local_favorite": True,
        "lat": 35.6764,
        "lng": 139.7055
    },
    {
        "name": "Odaiba",
        "destination": "Tokyo",
        "category": "Observation",
        "rating": 4.5,
        "review_count": 16000,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1496545672447-f699b503d270?w=800&q=80",
        "description": "Artificial island with shopping, entertainment, and views of Tokyo Bay and Rainbow Bridge.",
        "scout_tip": "Take the Yurikamome monorail for scenic views. Visit at night to see the Rainbow Bridge illuminated.",
        "is_local_favorite": False,
        "lat": 35.6300,
        "lng": 139.7800
    },
    {
        "name": "Shibuya Crossing",
        "destination": "Tokyo",
        "category": "Observation",
        "rating": 4.6,
        "review_count": 35000,
        "price_point": "Free",
        "image_url": "https://images.unsplash.com/photo-1551650975-87deedd944c3?w=800&q=80",
        "description": "World's busiest intersection. Watch thousands of people cross in perfect synchronization.",
        "scout_tip": "Best view is from the Starbucks on the second floor of the Tsutaya building. Go early or expect a wait.",
        "is_local_favorite": False,
        "lat": 35.6598,
        "lng": 139.7006
    },
    {
        "name": "Tokyo Imperial Palace",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.5,
        "review_count": 21000,
        "price_point": "Free",
        "image_url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800&q=80",
        "description": "Former Edo Castle and current residence of the Emperor. Beautiful gardens and historic architecture.",
        "scout_tip": "The East Gardens are open to the public and free. Book a guided tour in advance to see the inner grounds.",
        "is_local_favorite": False,
        "lat": 35.6852,
        "lng": 139.7528
    },
    {
        "name": "Ginza Shopping District",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.6,
        "review_count": 17000,
        "price_point": "$$$",
        "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80",
        "description": "Tokyo's upscale shopping district with luxury brands, department stores, and fine dining.",
        "scout_tip": "Pedestrian paradise on weekends (noon-5 PM). Even if not shopping, it's worth a stroll for the architecture.",
        "is_local_favorite": False,
        "lat": 35.6719,
        "lng": 139.7654
    },
    {
        "name": "Onsen (Hot Spring) Experience",
        "destination": "Tokyo",
        "category": "Relaxation",
        "rating": 4.8,
        "review_count": 8900,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=800&q=80",
        "description": "Traditional Japanese hot spring bath. Perfect way to relax after a long day of exploring Tokyo.",
        "scout_tip": "Tattoos are often not allowed. Check policies beforehand. Follow proper onsen etiquette (wash before entering).",
        "is_local_favorite": True,
        "lat": 35.6762,
        "lng": 139.6503
    },
    {
        "name": "Akihabara Electric Town",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.4,
        "review_count": 25000,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1580064003296-29deb3521370?w=800&q=80",
        "description": "Mecca for electronics, anime, and gaming culture. Multi-story arcades and specialty shops.",
        "scout_tip": "Bargain hunting is key. Check multiple stores for the best prices. Visit on Sundays when the main street is pedestrian-only.",
        "is_local_favorite": False,
        "lat": 35.6984,
        "lng": 139.7731
    },
    {
        "name": "Tokyo Station Ramen Street",
        "destination": "Tokyo",
        "category": "Food & Drink",
        "rating": 4.6,
        "review_count": 11000,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1569718212165-3a8278d5f624?w=800&q=80",
        "description": "Underground food area featuring 8 famous ramen shops from across Japan. Each with their own regional style.",
        "scout_tip": "Lines can be long during lunch and dinner. Try Rokurinsha for thick tsukemen (dipping ramen).",
        "is_local_favorite": True,
        "lat": 35.6813,
        "lng": 139.7671
    },
    {
        "name": "Yoyogi Park",
        "destination": "Tokyo",
        "category": "Relaxation",
        "rating": 4.5,
        "review_count": 13000,
        "price_point": "Free",
        "image_url": "https://images.unsplash.com/photo-1522093007474-d86e9bf7ba6f?w=800&q=80",
        "description": "Large park perfect for picnics, jogging, or people-watching. Popular on weekends with festivals and events.",
        "scout_tip": "Sunday afternoons often feature live music and dance performances. Bring a blanket for a picnic.",
        "is_local_favorite": False,
        "lat": 35.6697,
        "lng": 139.6980
    },
    {
        "name": "Kabukicho District",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.3,
        "review_count": 15000,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1509453729905-d6a85a5a2a3e?w=800&q=80",
        "description": "Tokyo's entertainment district with restaurants, bars, and nightlife. Safe to explore, especially the main streets.",
        "scout_tip": "Stick to main streets if unsure. Many themed cafes and restaurants offer unique experiences. Be cautious of touts.",
        "is_local_favorite": False,
        "lat": 35.6938,
        "lng": 139.7034
    },
    {
        "name": "Roppongi Hills",
        "destination": "Tokyo",
        "category": "Observation",
        "rating": 4.5,
        "review_count": 19000,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800&q=80",
        "description": "Modern complex with shopping, dining, and Tokyo City View observation deck with impressive cityscape views.",
        "scout_tip": "Visit the Tokyo City View observatory (52nd floor) for 360-degree views. Less crowded than Skytree.",
        "is_local_favorite": False,
        "lat": 35.6628,
        "lng": 139.7314
    },
    {
        "name": "Kappabashi Kitchen Town",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.6,
        "review_count": 5700,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1556910096-6f5e72db6803?w=800&q=80",
        "description": "Kitchen supply district with everything from professional knives to plastic food replicas. Unique Tokyo shopping experience.",
        "scout_tip": "Great place to buy Japanese kitchen knives as souvenirs. Bargaining is not common, prices are usually fixed.",
        "is_local_favorite": False,
        "lat": 35.7014,
        "lng": 139.7899
    },
    {
        "name": "Tsukishima Monjayaki Street",
        "destination": "Tokyo",
        "category": "Food & Drink",
        "rating": 4.7,
        "review_count": 3800,
        "price_point": "$$",
        "image_url": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800&q=80",
        "description": "Tokyo's version of okonomiyaki. This runny, pancake-like dish is a local specialty you won't find elsewhere.",
        "scout_tip": "Monjayaki is cooked on a hotplate at your table. Many shops have English menus. Try the mentaiko (spicy cod roe) version.",
        "is_local_favorite": True,
        "lat": 35.6628,
        "lng": 139.7850
    },
    {
        "name": "Nakameguro Cherry Blossoms",
        "destination": "Tokyo",
        "category": "Relaxation",
        "rating": 4.8,
        "review_count": 7200,
        "price_point": "Free",
        "image_url": "https://images.unsplash.com/photo-1522383225653-ed111181a951?w=800&q=80",
        "description": "Scenic canal lined with cherry trees. One of Tokyo's best spots for hanami (cherry blossom viewing) in spring.",
        "scout_tip": "Peak bloom is usually late March to early April. Arrive early morning or late evening to avoid crowds. Evening illuminations are beautiful.",
        "is_local_favorite": True,
        "lat": 35.6497,
        "lng": 139.6944
    },
    {
        "name": "Hamarikyu Gardens",
        "destination": "Tokyo",
        "category": "Relaxation",
        "rating": 4.6,
        "review_count": 9100,
        "price_point": "$",
        "image_url": "https://images.unsplash.com/photo-1549144511-f099e773c147?w=800&q=80",
        "description": "Beautiful Japanese landscape garden with a tidal pond and traditional tea house. Peaceful oasis in central Tokyo.",
        "scout_tip": "Visit the tea house on the island in the pond. Best time is autumn when the garden features special illuminations.",
        "is_local_favorite": False,
        "lat": 35.6586,
        "lng": 139.7744
    },
    {
        "name": "Tokyo DisneySea",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.7,
        "review_count": 45000,
        "price_point": "$$$",
        "image_url": "https://images.unsplash.com/photo-1519689680058-324335c77eba?w=800&q=80",
        "description": "Unique theme park with nautical exploration theme. Themed lands like Mysterious Island and Mermaid Lagoon.",
        "scout_tip": "Buy tickets online in advance. Arrive 30 minutes before opening. Use FastPass for popular rides.",
        "is_local_favorite": False,
        "lat": 35.6273,
        "lng": 139.8889
    },
    {
        "name": "Omotesando Hills",
        "destination": "Tokyo",
        "category": "Adventure",
        "rating": 4.6,
        "review_count": 8500,
        "price_point": "$$$",
        "image_url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=800&q=80",
        "description": "Architectural marvel by Tadao Ando. Upscale shopping center with luxury brands and modern design.",
        "scout_tip": "Even if not shopping, worth visiting for the architecture. The spiral ramps create a unique shopping experience.",
        "is_local_favorite": False,
        "lat": 35.6689,
        "lng": 139.7083
    }
]

def seed_attractions():
    """Seed attractions table with Tokyo data"""
    print("Seeding attractions...")
    
    try:
        # Check if attractions already exist
        existing = supabase.table("attractions").select("id").eq("destination", "Tokyo").limit(1).execute()
        if existing.data:
            response = input(f"Found existing Tokyo attractions. Overwrite? (y/N): ")
            if response.lower() != 'y':
                print("Skipping attractions seed.")
                return
        
        # Insert attractions
        count = 0
        for attraction in TOKYO_ATTRACTIONS:
            try:
                result = supabase.table("attractions").insert(attraction).execute()
                print(f"✓ Added: {attraction['name']}")
                count += 1
            except Exception as e:
                print(f"✗ Error adding {attraction['name']}: {str(e)}")
        
        print(f"\n✓ Successfully seeded {count} Tokyo attractions!")
    except Exception as e:
        print(f"✗ Error seeding attractions: {str(e)}")

def seed_demo_trip():
    """Create a demo trip so the dashboard isn't empty"""
    print("\nCreating demo trip...")
    
    try:
        # Check if demo trip exists
        existing = supabase.table("trips").select("id").eq("user_id", DEMO_USER_ID).eq("name", "Tokyo Fall 2024").execute()
        if existing.data:
            print("Demo trip already exists. Skipping.")
            return existing.data[0]["id"]
        
        # Create demo trip (Oct 12 - Oct 20, 2024)
        trip_start = date.today().replace(month=10, day=12) if date.today().month <= 10 else date.today().replace(year=date.today().year + 1, month=10, day=12)
        trip_end = trip_start + timedelta(days=8)
        
        trip_data = {
            "name": "Tokyo Fall 2024",
            "destination": "Tokyo",
            "start_date": str(trip_start),
            "end_date": str(trip_end),
            "budget_limit": 1200.00,
            "user_id": DEMO_USER_ID
        }
        
        trip_result = supabase.table("trips").insert(trip_data).execute()
        if not trip_result.data:
            raise Exception("Failed to create trip")
        
        trip_id = trip_result.data[0]["id"]
        print(f"✓ Created trip: {trip_data['name']} (ID: {trip_id})")
        
        # Get some attractions for the itinerary
        attractions_result = supabase.table("attractions").select("id, name").eq("destination", "Tokyo").limit(10).execute()
        
        # Create demo participants
        participants = [
            {"trip_id": trip_id, "name": "Niko Bonatsos", "email": "niko@example.com", "status": "accepted"},
            {"trip_id": trip_id, "name": "Cory Levy", "email": "cory@example.com", "status": "accepted"},
        ]
        
        for participant in participants:
            try:
                supabase.table("trip_participants").insert(participant).execute()
            except:
                pass  # Ignore duplicates
        
        print(f"✓ Added {len(participants)} participants to trip")
        print(f"\n✓ Demo trip created successfully!")
        
        return trip_id
    except Exception as e:
        print(f"✗ Error creating demo trip: {str(e)}")
        return None

def main():
    """Main seed function"""
    print("=" * 60)
    print("Navi Travel Planning - Database Seed Script")
    print("=" * 60)
    
    seed_attractions()
    seed_demo_trip()
    
    print("\n" + "=" * 60)
    print("Seed complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
