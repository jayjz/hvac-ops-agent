use hvac_ops;

db.inventory.insertMany([
  {
    "sku": "FILTER-001",
    "name": "Air Filter 14x25",
    "quantity": 4,
    "reorder_point": 15,
    "unit_cost": 12.99,
    "category": "Filters"
  },
  {
    "sku": "CAP-5TON",
    "name": "5-Ton Compressor Capacitor",
    "quantity": 2,
    "reorder_point": 8,
    "unit_cost": 45.0,
    "category": "Capacitors"
  }
]);

db.jobs.insertMany([
  {
    "job_id": "JOB-001",
    "job_type": "AC Repair",
    "customer_name": "Smith Residence",
    "scheduled_date": "2026-06-10T10:00:00Z",
    "status": "scheduled",
    "estimated_hours": 4.5,
    "customer_id": "CUST-001",
    "urgency": "high"
  }
]);

db.invoices.insertMany([
  {
    "invoice_id": "INV-001",
    "job_id": "JOB-001",
    "amount": 1250.0,
    "due_date": "2026-05-15T00:00:00Z",
    "status": "overdue",
    "days_overdue": 21
  }
]);

print("MongoDB hvac_ops initialized with sample data matching Pydantic schemas (InventoryItem, JobDocument, Invoice).");