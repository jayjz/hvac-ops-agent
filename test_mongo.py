"""Test MongoDB connectivity and basic operations for HVAC OpsForge."""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.tools.mongodb_tools import MongoDBTools
from core.agents.specialists import InventoryForecasterAgent
import pytest


def test_mongodb_connection():
    """Test basic MongoDB connectivity."""
    print("Testing MongoDB connection...")
    
    # Initialize MongoDB tools
    mongo = MongoDBTools()
    
    try:
        # Try to connect
        db = mongo.connect()
        print(f"✓ Connected to MongoDB database: {db.name}")
        
        # List collections
        collections = db.list_collection_names()
        print(f"✓ Available collections: {collections}")
        
        # Test queries (will return empty if no data, but should not error)
        print("\nTesting queries...")
        
        jobs = mongo.get_upcoming_jobs(days_ahead=30)
        print(f"✓ Upcoming jobs query successful: {len(jobs)} jobs found")
        
        inventory = mongo.get_inventory_levels(low_stock_threshold=10)
        print(f"✓ Inventory query successful: {len(inventory)} low-stock items found")
        
        invoices = mongo.get_overdue_invoices(days_overdue=30)
        print(f"✓ Overdue invoices query successful: {len(invoices)} invoices found")
        
        print("\n✅ All MongoDB tests passed!")
        print("\nNote: If collections are empty, populate with sample data using:")
        print("  - jobs: upcoming HVAC service calls")
        print("  - inventory: parts and stock levels")
        print("  - invoices: customer invoices with due dates")
        print("  - technicians: technician profiles and schedules")
        
        return True
        
    except Exception as exc:
        print(f"✗ MongoDB connection failed: {exc}")
        print("\nTo fix:")
        print("1. Ensure MongoDB is running (local or Atlas)")
        print("2. Set MONGO_URI environment variable if using Atlas:")
        print("   export MONGO_URI='mongodb+srv://user:***@cluster.mongodb.net/'")
        print("3. Or update core/tools/mongodb_tools.py with your connection string")
        return False
        
    finally:
        mongo.disconnect()
        print("\n✓ Disconnected from MongoDB")


def create_sample_data():
    """Create sample data for testing (optional)."""
    print("\n" + "="*60)
    print("Creating sample data...")
    print("="*60)
    
    mongo = MongoDBTools()
    
    try:
        db = mongo.connect()
        
        # Sample jobs
        jobs_collection = db["jobs"]
        if jobs_collection.count_documents({}) == 0:
            sample_jobs = [
                {
                    "_id": "job_001",
                    "job_type": "heat_pump_install",
                    "customer_id": "cust_001",
                    "customer_name": "ABC Manufacturing",
                    "scheduled_date": datetime.utcnow() + timedelta(days=3),
                    "status": "scheduled",
                    "assigned_technician": "tech_001",
                    "estimated_duration_hours": 8,
                    "parts_required": ["HP-001", "LINESET-50", "PAD-CONC"],
                },
                {
                    "_id": "job_002",
                    "job_type": "ac_repair",
                    "customer_id": "cust_002",
                    "customer_name": "XYZ Office Complex",
                    "scheduled_date": datetime.utcnow() + timedelta(days=5),
                    "status": "scheduled",
                    "assigned_technician": "tech_002",
                    "estimated_duration_hours": 3,
                    "parts_required": ["FILTER-01", "REFRIG-R410A"],
                },
            ]
            jobs_collection.insert_many(sample_jobs)
            print(f"✓ Inserted {len(sample_jobs)} sample jobs")
        else:
            print("✓ Jobs collection already has data")
        
        # Sample inventory
        inventory_collection = db["inventory"]
        if inventory_collection.count_documents({}) == 0:
            sample_inventory = [
                {
                    "sku": "HP-001",
                    "name": "Heat Pump Unit 3-Ton",
                    "quantity": 2,
                    "reorder_point": 3,
                    "unit_cost": 2500.00,
                    "supplier": "HVAC Supply Co",
                },
                {
                    "sku": "FILTER-01",
                    "name": "Air Filter 20x25x1",
                    "quantity": 15,
                    "reorder_point": 20,
                    "unit_cost": 12.50,
                    "supplier": "Filter Wholesale",
                },
                {
                    "sku": "REFRIG-R410A",
                    "name": "R410A Refrigerant 25lb",
                    "quantity": 5,
                    "reorder_point": 10,
                    "unit_cost": 185.00,
                    "supplier": "Refrigerant Direct",
                },
            ]
            inventory_collection.insert_many(sample_inventory)
            print(f"✓ Inserted {len(sample_inventory)} sample inventory items")
        else:
            print("✓ Inventory collection already has data")
        
        # Sample invoices
        invoices_collection = db["invoices"]
        if invoices_collection.count_documents({}) == 0:
            sample_invoices = [
                {
                    "_id": "inv_001",
                    "customer_id": "cust_001",
                    "customer_name": "ABC Manufacturing",
                    "amount": 4500.00,
                    "invoice_date": datetime.utcnow() - timedelta(days=60),
                    "due_date": datetime.utcnow() - timedelta(days=30),
                    "status": "overdue",
                    "job_id": "job_001",
                },
                {
                    "_id": "inv_002",
                    "customer_id": "cust_003",
                    "customer_name": "Downtown Retail",
                    "amount": 1200.00,
                    "invoice_date": datetime.utcnow() - timedelta(days=45),
                    "due_date": datetime.utcnow() - timedelta(days=15),
                    "status": "sent",
                    "job_id": "job_003",
                },
            ]
            invoices_collection.insert_many(sample_invoices)
            print(f"✓ Inserted {len(sample_invoices)} sample invoices")
        else:
            print("✓ Invoices collection already has data")
        
        print("\n✅ Sample data creation complete!")
        
    except Exception as exc:
        print(f"✗ Failed to create sample data: {exc}")
    finally:
        mongo.disconnect()


# TDD RED PHASE for generate_pre_departure_report (hvac-parts-availability-checker skill)
# Tests define expected Markdown report with summary, risk flags, table, recommendations.
# Surgical addition ONLY to test_mongo.py per rules. No code in specialists.py or mongodb_tools.py yet.
# Reuses existing InventoryForecasterAgent synthetic paths, _forecast_inventory_needs, MongoDBTools fallbacks.
# These will fail (AttributeError on missing method) - mandatory RED per test-driven-development skill.


def test_generate_pre_departure_report_returns_markdown_with_all_sections():
    """RED: Method must produce structured report with all sections and risk indicators.
    Fails because generate_pre_departure_report does not exist yet on InventoryForecasterAgent.
    """
    agent = InventoryForecasterAgent()
    jobs = ["job_001", "job_002"]
    report = agent.generate_pre_departure_report(jobs)
    assert isinstance(report, str), "Must return string Markdown"
    assert "# Pre-Departure Parts Availability Report" in report, "Must have standard header"
    assert "Summary" in report, "Must include executive summary with job/risk counts"
    assert "Risk Flags" in report, "Must have risk section with ❌/🟡/✅"
    assert "Parts Status" in report, "Must include Markdown table of SKUs/required/current/shortage"
    assert "Immediate Actions" in report or "recommendations" in report.lower(), "Must have actionable recommendations for techs"
    assert any(f in report for f in ["❌", "Critical", "🟡", "Warning", "✅", "OK"]), "Must use visual risk indicators"


def test_generate_pre_departure_report_handles_synthetic_fallback_and_validation():
    """RED: Must handle synthetic fallback (existing in specialists.py + mongodb_tools.py), raise on bad input.
    Tests integration with _get_synthetic_jobs, get_upcoming_jobs fallback, error handling per skill.
    """
    agent = InventoryForecasterAgent()
    # Synthetic path (no real Mongo)
    report = agent.generate_pre_departure_report(["ac_repair"])
    assert isinstance(report, str)
    assert any(word in report.lower() for word in ["synthetic", "fallback", "cached", "using sample"]), "Should document fallback"
    # Validation edge case
    with pytest.raises((ValueError, TypeError, AttributeError)):
        agent.generate_pre_departure_report([])  # Empty should trigger validation per skill


if __name__ == "__main__":
    print("="*60)
    print("HVAC OpsForge - MongoDB Test Suite")
    print("="*60)
    print()
    
    success = test_mongodb_connection()
    
    if success:
        response = input("\nCreate sample data for testing? (y/n): ")
        if response.lower() == 'y':
            create_sample_data()
    
    print("\n" + "="*60)
    print("Test complete")
    print("="*60)
