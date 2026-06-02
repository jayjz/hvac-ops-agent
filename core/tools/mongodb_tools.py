# core/tools/mongodb_tools.py
# Clean MongoDB tools for HVAC OpsForge Agent

from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime, timedelta
from typing import List, Dict, Any

load_dotenv()

class MongoDBTools:
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self):
        """Connect to MongoDB Atlas"""
        try:
            uri = os.getenv("MONGO_URI")
            if not uri:
                raise ValueError("MONGO_URI not found in .env")
            
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client.hvac_ops
            print("✅ MongoDB connected successfully")
            return self.client
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            return None

    def get_upcoming_jobs(self, days: int = 14) -> List[Dict]:
        """Get upcoming jobs"""
        try:
            if not self.db:
                self.connect()
            if not self.db:
                return self._synthetic_upcoming_jobs()
            
            cutoff = datetime.now() + timedelta(days=days)
            jobs = list(self.db.jobs.find({
                "scheduled_date": {"$lte": cutoff},
                "status": {"$in": ["scheduled", "confirmed", "in_progress"]}
            }).sort("scheduled_date", 1).limit(50))
            
            return jobs
        except Exception:
            return self._synthetic_upcoming_jobs()

    def get_low_inventory(self, threshold_multiplier: float = 1.2) -> List[Dict]:
        """Get low stock inventory items"""
        try:
            if not self.db:
                self.connect()
            if not self.db:
                return self._synthetic_low_inventory()
            
            pipeline = [
                {"$addFields": {
                    "threshold": {"$multiply": ["$reorder_point", threshold_multiplier]}
                }},
                {"$match": {"quantity": {"$lte": {"$multiply": ["$reorder_point", threshold_multiplier]}}}},
                {"$sort": {"quantity": 1}},
                {"$limit": 50}
            ]
            return list(self.db.inventory.aggregate(pipeline))
        except Exception:
            return self._synthetic_low_inventory()

    def get_overdue_invoices(self, days: int = 30) -> List[Dict]:
        """Get overdue invoices"""
        try:
            if not self.db:
                self.connect()
            if not self.db:
                return self._synthetic_overdue_invoices()
            
            cutoff = datetime.now() - timedelta(days=days)
            invoices = list(self.db.invoices.find({
                "due_date": {"$lte": cutoff},
                "status": {"$in": ["sent", "pending", "overdue"]},
                "paid_date": None
            }).sort("due_date", 1).limit(100))
            
            return invoices
        except Exception:
            return self._synthetic_overdue_invoices()

    # Synthetic fallbacks
    def _synthetic_upcoming_jobs(self):
        return [
            {"job_id": "JOB-001", "customer": "Smith Residence", "type": "Heat Pump Install", "scheduled_date": datetime.now() + timedelta(days=3), "status": "scheduled"},
            {"job_id": "JOB-002", "customer": "Green Complex", "type": "AC Maintenance", "scheduled_date": datetime.now() + timedelta(days=1), "status": "confirmed"}
        ]

    def _synthetic_low_inventory(self):
        return [
            {"name": "Heat Pump Unit", "quantity": 1, "reorder_point": 3},
            {"name": "Filters", "quantity": 8, "reorder_point": 20}
        ]

    def _synthetic_overdue_invoices(self):
        return [
            {"invoice_id": "INV-001", "customer": "Johnson Family", "amount": 2450, "due_date": datetime.now() - timedelta(days=45), "days_overdue": 45}
        ]