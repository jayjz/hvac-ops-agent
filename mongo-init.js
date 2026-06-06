use hvac_ops;

db.inventory.insertMany([
  { "sku": "FILTER-001", "name": "Air Filter 14x25", "quantity": 4, "reorder_point": 15, "unit_cost": 12.99, "category": "Filters" },
  { "sku": "CAP-5TON", "name": "5-Ton Compressor Capacitor", "quantity": 2, "reorder_point": 8, "unit_cost": 45.0, "category": "Capacitors" },
  { "sku": "HP-001", "name": "Heat Pump Unit 3-Ton", "quantity": 1, "reorder_point": 3, "unit_cost": 1200.0, "category": "Units" },
  { "sku": "TXV-3TON", "name": "TXV Valve 3-Ton", "quantity": 5, "reorder_point": 8, "unit_cost": 65.0, "category": "Valves" },
  { "sku": "REFRIG-R410A-25", "name": "R410A Refrigerant 25lb", "quantity": 8, "reorder_point": 12, "unit_cost": 85.0, "category": "Refrigerant" }
]);

db.jobs.insertMany([
  { "job_id": "JOB-001", "job_type": "AC Repair", "customer_name": "Smith Residence", "scheduled_date": "2026-06-10T10:00:00Z", "status": "scheduled", "estimated_hours": 4.5, "customer_id": "CUST-001", "urgency": "high", "customer_lat": 42.7125, "customer_lon": -71.4523 },
  { "job_id": "JOB-002", "job_type": "Furnace Install", "customer_name": "ABC Manufacturing", "scheduled_date": "2026-06-10T13:00:00Z", "status": "scheduled", "estimated_hours": 6.0, "customer_id": "CUST-002", "urgency": "medium", "customer_lat": 42.7812, "customer_lon": -71.4128 },
  { "job_id": "JOB-003", "job_type": "Heat Pump Service", "customer_name": "XYZ Office Complex", "scheduled_date": "2026-06-11T09:00:00Z", "status": "scheduled", "estimated_hours": 3.5, "customer_id": "CUST-003", "urgency": "high", "customer_lat": 42.7341, "customer_lon": -71.4819 },
  { "job_id": "JOB-004", "job_type": "Maintenance", "customer_name": "Downtown Retail", "scheduled_date": "2026-06-11T14:00:00Z", "status": "scheduled", "estimated_hours": 2.0, "customer_id": "CUST-004", "urgency": "low", "customer_lat": 42.7654, "customer_lon": -71.4398 },
  { "job_id": "JOB-005", "job_type": "AC Repair", "customer_name": "Johnson Family", "scheduled_date": "2026-06-12T11:00:00Z", "status": "scheduled", "estimated_hours": 5.0, "customer_id": "CUST-005", "urgency": "high", "customer_lat": 42.7956, "customer_lon": -71.3852 },
  { "job_id": "JOB-006", "job_type": "Furnace Install", "customer_name": "Hudson School", "scheduled_date": "2026-06-12T15:00:00Z", "status": "scheduled", "estimated_hours": 7.5, "customer_id": "CUST-006", "urgency": "medium", "customer_lat": 42.  7648, "customer_lon": -71.  4551 },
  { "job_id": "JOB-007", "job_type": "Maintenance", "customer_name": "Tech Park Inc", "scheduled_date": "2026-06-13T08:00:00Z", "status": "scheduled", "estimated_hours": 4.0, "customer_id": "CUST-007", "urgency": "high", "customer_lat": 42.  7234, "customer_lon": -71.  4729 },
  { "job_id": "JOB-008", "job_type": "Heat Pump Service", "customer_name": "RiverView Condos", "scheduled_date": "2026-06-13T10:00:00Z", "status": "scheduled", "estimated_hours": 3.0, "customer_id": "CUST-008", "urgency": "medium", "customer_lat": 42.  7519, "customer_lon": -71.  4187 },
  { "job_id": "JOB-009", "job_type": "AC Repair", "customer_name": "Baker Residence", "scheduled_date": "2026-06-14T09:00:00Z", "status": "scheduled", "estimated_hours": 4.0, "customer_id": "CUST-009", "urgency": "high", "customer_lat": 42.  7892, "customer_lon": -71.  3921 },
  { "job_id": "JOB-010", "job_type": "Maintenance", "customer_name": "Nashua Plaza", "scheduled_date": "2026-06-14T13:00:00Z", "status": "scheduled", "estimated_hours": 2.5, "customer_id": "CUST-010", "urgency": "low", "customer_lat": 42.  7416, "customer_lon": -71.  4634 },
  { "job_id": "JOB-011", "job_type": "Furnace Install", "customer_name": "Elm Street Offices", "scheduled_date": "2026-06-15T11:00:00Z", "status": "scheduled", "estimated_hours": 6.0, "customer_id": "CUST-011", "urgency": "medium", "customer_lat": 42.  7765, "customer_lon": -71.  4298 },
  { "job_id": "JOB-012", "job_type": "Heat Pump Service", "customer_name": "Pine Grove Homes", "scheduled_date": "2026-06-15T14:00:00Z", "status": "scheduled", "estimated_hours": 3.5, "customer_id": "CUST-012", "urgency": "high", "customer_lat": 42.  7582, "customer_lon": -71.  4476 }
]);

db.invoices.insertMany([
  { "invoice_id": "INV-001", "job_id": "JOB-001", "amount": 1250.0, "due_date": "2026-05-15T00:00:00Z", "status": "overdue", "days_overdue": 21, "customer_name": "Smith Residence" },
  { "invoice_id": "INV-002", "job_id": "JOB-003", "amount": 875.0, "due_date": "2026-05-20T00:00:00Z", "status": "overdue", "days_overdue": 16, "customer_name": "XYZ Office Complex" },
  { "invoice_id": "INV-003", "job_id": "JOB-005", "amount": 2100.0, "due_date": "2026-05-10T00:00:00Z", "status": "overdue", "days_overdue": 26, "customer_name": "Johnson Family" },
  { "invoice_id": "INV-004", "job_id": "JOB-007", "amount": 650.0, "due_date": "2026-05-25T00:00:00Z", "status": "overdue", "days_overdue": 11, "customer_name": "Tech Park Inc" }
]);

print("MongoDB hvac_ops initialized with RICH realistic mock data (12+ jobs with Nashua/Hudson NH lat/lon ~42.7x/-71.4x, low inventory, overdue AR invoices, matching Pydantic schemas). Ready for Owner ROI Simulator.");
