# seed_sample_data.py
# purpose: insert realistic hvac sample data into mongodb so the agent has something to work with

from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime, timedelta
import random

load_dotenv()
uri = os.getenv("MONGO_URI")

client = MongoClient(uri)
db = client.hvac_ops  # using database name "hvac_ops"

# Clear existing collections for clean start
db.jobs.drop()
db.inventory.drop()
db.customers.drop()

# === SAMPLE JOBS ===
jobs = [
    {
        "job_id": "JOB-2026-001",
        "customer": "Smith Residence",
        "type": "Heat Pump Installation",
        "status": "scheduled",
        "scheduled_date": datetime.now() + timedelta(days=2),
        "technician": "Mike Torres",
        "parts_needed": ["Heat Pump Unit", "Thermostat"],
        "estimated_cost": 4500,
        "ar_status": "pending"
    },
    {
        "job_id": "JOB-2026-002",
        "customer": "Green Office Complex",
        "type": "AC Maintenance",
        "status": "in_progress",
        "scheduled_date": datetime.now() + timedelta(days=1),
        "technician": "Sara Chen",
        "parts_needed": ["Filters", "Refrigerant"],
        "estimated_cost": 850,
        "ar_status": "overdue"
    },
    {
        "job_id": "JOB-2026-003",
        "customer": "Johnson Family",
        "type": "Furnace Repair",
        "status": "completed",
        "scheduled_date": datetime.now() - timedelta(days=5),
        "technician": "Mike Torres",
        "parts_needed": ["Igniter"],
        "estimated_cost": 620,
        "ar_status": "paid"
    }
]

db.jobs.insert_many(jobs)
print(f"✅ Inserted {len(jobs)} sample jobs")

# === SAMPLE INVENTORY ===
inventory = [
    {"part": "Heat Pump Unit", "stock": 3, "min_threshold": 2, "last_reorder": datetime.now() - timedelta(days=30)},
    {"part": "Thermostat", "stock": 8, "min_threshold": 5, "last_reorder": None},
    {"part": "Filters", "stock": 12, "min_threshold": 20, "last_reorder": datetime.now() - timedelta(days=10)},
    {"part": "Refrigerant", "stock": 4, "min_threshold": 6, "last_reorder": None},
]

db.inventory.insert_many(inventory)
print(f"✅ Inserted {len(inventory)} inventory items")

print("🎉 Sample HVAC data seeded successfully!")
print("You can now query these collections.")