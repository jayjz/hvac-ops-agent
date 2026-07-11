import json
import random
from datetime import datetime, timedelta, timezone

def generate_enterprise_demo():
    # 1. Technicians: 15 distinct profiles
    roles = ["Lead Tech", "Senior Tech", "Apprentice", "Controls Specialist"]
    techs = [
        {"id": f"TCH-{i:03d}", "name": f"Tech {i}", "role": random.choice(roles), "status": "Available"} 
        for i in range(1, 16)
    ]

    # 2. Jobs: High density, varied types
    job_types = ["HVAC_Maintenance", "Emergency_Repair", "Full_Install", "BAS_Retrofit"]
    jobs = []
    for i in range(1, 21):
        jobs.append({
            "job_id": f"JOB-{1000+i}",
            "job_type": random.choice(job_types),
            "customer_name": f"Enterprise Client {i}",
            "scheduled_date": (datetime.now(timezone.utc) + timedelta(days=random.randint(0, 5))).isoformat(),
            "status": random.choice(["scheduled", "confirmed", "in_progress"]),
            "estimated_hours": random.uniform(2.0, 12.0),
            "assigned_tech": f"TCH-{random.randint(1, 15):03d}"
        })

    # 3. Inventory: 20 SKUs, mixing critical/non-critical to trigger reorder logic
    skus = ["COMP-44", "FLTR-2025", "THERM-X1", "VALVE-TXV", "BELT-48", "MTR-0.5HP"]
    inventory = [
        {"sku": s, "name": f"Part {s}", "quantity": random.randint(0, 20), "reorder_point": 10, "unit_cost": random.uniform(20.0, 500.0), "category": "Stock"}
        for s in skus
    ]

    # 4. Invoices: Aged and active to test AR Collector
    invoices = [
        {
            "invoice_id": f"INV-{2000+i}",
            "customer_name": f"Enterprise Client {i}",
            "amount": random.uniform(500.0, 15000.0),
            "days_overdue": random.randint(0, 60),
            "status": "overdue" if random.random() > 0.5 else "sent"
        }
        for i in range(1, 15)
    ]

    data = {"inventory": inventory, "jobs": jobs, "invoices": invoices, "technicians": techs}
    
    with open("memory/demo_data.json", "w") as f:
        json.dump(data, f, indent=4)
    print(f"Generated robust simulation: 15 Techs, {len(jobs)} Jobs, {len(invoices)} Invoices.")

if __name__ == "__main__":
    generate_enterprise_demo()