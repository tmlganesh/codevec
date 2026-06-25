"""
Seed script: generates 200,000 products with fast bulk inserts.

Usage: python seed.py

Strategy:
  - Builds rows in Python as dicts (fast)
  - Uses SQLAlchemy Core bulk_insert_mappings in batches of 5,000
  - Total insert time: ~30-60 seconds depending on network latency to Supabase
"""

import uuid
import random
import time
from datetime import datetime, timedelta, timezone
from app.database import engine, Base, SessionLocal
from app.models import Product

# --- Configuration ---
TOTAL_PRODUCTS = 200_000
BATCH_SIZE = 5_000

CATEGORIES = [
    "Electronics", "Clothing", "Home & Kitchen", "Books", "Sports",
    "Toys & Games", "Health & Beauty", "Automotive", "Garden & Outdoor",
    "Office Supplies", "Pet Supplies", "Food & Grocery",
]

ADJECTIVES = [
    "Premium", "Ultra", "Pro", "Elite", "Classic", "Modern", "Compact",
    "Deluxe", "Smart", "Eco", "Turbo", "Max", "Mini", "Mega", "Super",
    "Advanced", "Essential", "Signature", "Limited", "Custom",
]

NOUNS = {
    "Electronics": ["Headphones", "Speaker", "Charger", "Cable", "Monitor", "Keyboard", "Mouse", "Webcam", "Tablet", "Router"],
    "Clothing": ["T-Shirt", "Jacket", "Hoodie", "Jeans", "Sneakers", "Cap", "Scarf", "Gloves", "Socks", "Belt"],
    "Home & Kitchen": ["Blender", "Toaster", "Lamp", "Cushion", "Vase", "Pan", "Knife Set", "Cutting Board", "Mug", "Towel"],
    "Books": ["Novel", "Cookbook", "Guide", "Manual", "Journal", "Planner", "Atlas", "Anthology", "Memoir", "Textbook"],
    "Sports": ["Yoga Mat", "Dumbbells", "Jump Rope", "Resistance Band", "Water Bottle", "Gym Bag", "Shin Guards", "Goggles", "Gloves", "Jersey"],
    "Toys & Games": ["Puzzle", "Board Game", "Action Figure", "Doll", "Building Set", "Card Game", "Drone", "RC Car", "Stuffed Animal", "Play Set"],
    "Health & Beauty": ["Moisturizer", "Shampoo", "Sunscreen", "Serum", "Lip Balm", "Face Mask", "Brush Set", "Nail Kit", "Perfume", "Lotion"],
    "Automotive": ["Floor Mat", "Phone Mount", "Dash Cam", "Air Freshener", "Seat Cover", "Tool Kit", "Jump Starter", "Tire Gauge", "Wax", "Polish"],
    "Garden & Outdoor": ["Planter", "Hose", "Shovel", "Gloves", "Seeds", "Lantern", "Hammock", "Grill", "Fire Pit", "Bird Feeder"],
    "Office Supplies": ["Notebook", "Pen Set", "Stapler", "Desk Organizer", "Whiteboard", "Marker Set", "Binder", "Paper Shredder", "Label Maker", "Tape Dispenser"],
    "Pet Supplies": ["Dog Bed", "Cat Toy", "Leash", "Food Bowl", "Collar", "Grooming Kit", "Treats", "Carrier", "Scratching Post", "Aquarium Filter"],
    "Food & Grocery": ["Coffee Beans", "Olive Oil", "Pasta", "Spice Set", "Granola", "Honey", "Tea Sampler", "Protein Bar", "Dried Fruit", "Hot Sauce"],
}

# Time range: products created over the last 365 days
NOW = datetime.now(timezone.utc)
OLDEST = NOW - timedelta(days=365)
TIME_RANGE_SECONDS = int((NOW - OLDEST).total_seconds())


def generate_product() -> dict:
    """Generate a single product as a dict for bulk insertion."""
    category = random.choice(CATEGORIES)
    adjective = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS[category])
    model_num = random.randint(100, 9999)

    created_at = OLDEST + timedelta(seconds=random.randint(0, TIME_RANGE_SECONDS))
    # updated_at is at or after created_at
    update_offset = random.randint(0, int((NOW - created_at).total_seconds()))
    updated_at = created_at + timedelta(seconds=update_offset)

    return {
        "id": uuid.uuid4(),
        "name": f"{adjective} {noun} {model_num}",
        "category": category,
        "price": round(random.uniform(1.99, 999.99), 2),
        "created_at": created_at,
        "updated_at": updated_at,
    }


def seed():
    print(f"Creating tables...")
    Base.metadata.create_all(bind=engine)

    print(f"Generating {TOTAL_PRODUCTS:,} products in batches of {BATCH_SIZE:,}...")
    start = time.time()
    session = SessionLocal()

    try:
        for batch_start in range(0, TOTAL_PRODUCTS, BATCH_SIZE):
            batch = [generate_product() for _ in range(BATCH_SIZE)]
            session.bulk_insert_mappings(Product, batch)
            session.commit()
            inserted = min(batch_start + BATCH_SIZE, TOTAL_PRODUCTS)
            elapsed = time.time() - start
            rate = inserted / elapsed
            print(f"  Inserted {inserted:>7,} / {TOTAL_PRODUCTS:,}  ({rate:,.0f} rows/sec)")

        total_time = time.time() - start
        print(f"\nDone. {TOTAL_PRODUCTS:,} products inserted in {total_time:.1f}s")
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
