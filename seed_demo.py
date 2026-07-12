# scripts/seed_demo_data.py
import json
import random
from datetime import datetime, timedelta, timezone

def generate_enterprise_demo():
    random.seed(101) # Locked seed for consistent demo presentations
    now = datetime.now(timezone.utc)

    # 1. Conglomerate Technician Roster
    roles = [
        "Senior Chiller Mechanic", "Controls & BAS Engineer", 
        "Commercial RTU Tech", "Lead Pipefitter", "Preventative Maintenance Tech"
    ]
    techs = [
        {"id": f"TCH-{i:03d}", "name": f"Tech {i}", "role": random.choice(roles), "status": "Dispatched"} 
        for i in range(1, 16)
    ]

    # 2. High-Volume Commercial Jobs
    job_types = ["Chiller Overhaul", "Emergency RTU Down", "BAS Controller Offline", "Quarterly PM", "Compressor Swap"]
    clients = ["Apex Logistics Hub", "Summit Medical Center", "Downtown Office Tower", "City Data Center", "Westside Mall"]
    
    jobs = []
    for i in range(1, 26): # 25 jobs for a busy dispatch board
        assigned_tech = f"TCH-{random.randint(1, 15):03d}"
        jobs.append({
            "job_id": f"JOB-{1000+i}",
            "job_type": random.choice(job_types),
            "customer_name": random.choice(clients),
            "scheduled_date": (now + timedelta(hours=random.randint(1, 48))).isoformat(),
            "status": random.choice(["dispatched", "in_progress", "parts_hold"]),
            "estimated_hours": round(random.uniform(2.0, 16.0), 1),
            "assigned_tech": assigned_tech,
            "priority": "High" if "Emergency" in job_types or "Data Center" in clients else "Normal"
        })

    # 3. Enterprise Inventory (High Cost, Critical Impact)
    skus = [
        ("COMP-100T", "100-Ton Centrifugal Compressor", 25000.00),
        ("VFD-480V", "480V Variable Frequency Drive", 3200.00),
        ("CTRL-JACE", "JACE 8000 Controller", 1850.00),
        ("R134A-CYL", "R-134a Refrigerant 30lb", 350.00),
        ("FLTR-MERV13", "MERV 13 Bulk Filter Pack", 120.00)
    ]
    inventory = []
    for sku, name, cost in skus:
        qty = random.randint(0, 5)
        inventory.append({
            "sku": sku, 
            "name": name, 
            "quantity": qty, 
            "reorder_point": 3, 
            "unit_cost": cost, 
            "status": "Critical Low" if qty == 0 else "In Stock"
        })

    # 4. Heavy AR Queue (Commercial Net-30/Net-60 terms)
    invoices = []
    for i in range(1, 12):
        days_late = random.randint(5, 90)
        invoices.append({
            "invoice_id": f"INV-{5000+i}",
            "customer_name": random.choice(clients),
            "amount": round(random.uniform(2500.0, 45000.0), 2),
            "days_overdue": days_late,
            "status": "Severely Overdue" if days_late > 60 else "Overdue",
            "due_date": (now - timedelta(days=days_late)).isoformat()
        })

    data = {"inventory": inventory, "jobs": jobs, "invoices": invoices, "technicians": techs}
    
    # Ensure directory exists
    import os
    os.makedirs("memory", exist_ok=True)
    
    with open("memory/demo_data.json", "w") as f:
        json.dump(data, f, indent=4)
    
    total_ar = sum(inv['amount'] for inv in invoices)
    print(f"Enterprise Data Seeded: 15 Techs | 25 Jobs | ${total_ar:,.2f} in Overdue AR.")

if __name__ == "__main__":
    generate_enterprise_demo()