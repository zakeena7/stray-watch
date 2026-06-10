"""
seed.py — Run this once to populate your database with realistic sample data.
Command: python seed.py

This creates:
  - 5 Chennai localities
  - 50 sample dogs spread across them with varied vaccination status
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, create_tables
from app.models import Locality, Dog
from datetime import datetime, timedelta
import random

# ── Sample data ───────────────────────────────────────────────────────────────

LOCALITIES = [
    {"name": "T. Nagar",     "lat": 13.0418, "lng": 80.2341},
    {"name": "Adyar",        "lat": 13.0012, "lng": 80.2565},
    {"name": "Anna Nagar",   "lat": 13.0850, "lng": 80.2101},
    {"name": "Mylapore",     "lat": 13.0336, "lng": 80.2687},
    {"name": "Velachery",    "lat": 12.9815, "lng": 80.2180},
]

COLORS = [
    "brown", "black", "white", "black and white", "brown and white",
    "golden", "grey", "tan", "dark brown", "cream"
]

SEXES = ["male", "female"]

NOTES_LIST = [
    "Friendly, often near the market",
    "Aggressive when approached, caution advised",
    "Travels in a pack of 3",
    "Ear notch visible — likely sterilized before",
    "Limping on front left leg, needs vet attention",
    "Often seen near the temple",
    "Very friendly with children",
    "Seen near the bus stop daily",
    None, None, None  # some dogs have no notes
]

def run_seed():
    create_tables()
    db = SessionLocal()

    # Check if already seeded
    existing = db.query(Locality).count()
    if existing >= 5:
        print("Database already has data. Clear it first if you want to reseed.")
        db.close()
        return

    print("Seeding localities...")
    locality_objects = []
    for i, loc_data in enumerate(LOCALITIES):
        # Vary last_survey dates to make risk scores interesting
        days_ago = random.choice([1, 3, 5, 8, 12])
        loc = Locality(
            name        = loc_data["name"],
            lat         = loc_data["lat"],
            lng         = loc_data["lng"],
            risk_score  = 0,  # will be recalculated by alert generator
            last_survey = datetime.utcnow() - timedelta(days=days_ago)
        )
        db.add(loc)
        db.flush()  # get the id without committing
        locality_objects.append(loc)
        print(f"  ✓ {loc.name} (id={loc.id})")

    print("\nSeeding dogs...")
    dog_count = 0

    # Distribution: T.Nagar=15, Adyar=10, Anna Nagar=12, Mylapore=8, Velachery=5
    distribution = [15, 10, 12, 8, 5]

    for loc, count in zip(locality_objects, distribution):
        for i in range(count):
            dog_count += 1
            is_vaccinated = random.random() < 0.45  # ~45% vaccinated overall

            # Vaccination dates
            vax_date   = None
            vax_expiry = None
            if is_vaccinated:
                months_ago = random.randint(1, 11)
                vax_date   = datetime.utcnow() - timedelta(days=months_ago * 30)
                vax_expiry = vax_date + timedelta(days=365)

            dog = Dog(
                dog_code    = f"DOG-{str(dog_count).zfill(4)}",
                locality_id = loc.id,
                sex         = random.choice(SEXES),
                color       = random.choice(COLORS),
                vaccinated  = is_vaccinated,
                vax_date    = vax_date,
                vax_expiry  = vax_expiry,
                sterilized  = random.random() < 0.3,  # 30% sterilized
                notes       = random.choice(NOTES_LIST),
            )
            db.add(dog)

        print(f"  ✓ {count} dogs added to {loc.name}")

    db.commit()
    db.close()

    print(f"\n✅ Seed complete!")
    print(f"   {len(LOCALITIES)} localities")
    print(f"   {dog_count} dogs")
    print(f"\nNow call POST /alerts/generate to calculate risk scores.")

if __name__ == "__main__":
    run_seed()
