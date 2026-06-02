"""MongoDB tools for HVAC OpsForge agent operations."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database


class MongoDBTools:
    """MongoDB operations for HVAC business data."""

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv(
            "MONGO_URI", "mongodb://localhost:27017/"
        )
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None

    def connect(self, db_name: str = "hvac_ops") -> Database:
        """Connect to MongoDB and return database handle."""
        if not self.client:
            self.client = MongoClient(self.connection_string)
        self.db = self.client[db_name]
        return self.db

    def disconnect(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    # Jobs Collection Operations
    def get_upcoming_jobs(
        self, days_ahead: int = 7, status: str = "scheduled"
    ) -> List[Dict[str, Any]]:
        """Get jobs scheduled in the next N days."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["jobs"]
        cutoff = datetime.utcnow() + timedelta(days=days_ahead)
        
        jobs = list(
            collection.find(
                {
                    "scheduled_date": {"$lte": cutoff},
                    "status": status,
                }
            ).sort("scheduled_date", 1)
        )
        return jobs

    def get_job_by_id(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific job by ID."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["jobs"]
        return collection.find_one({"_id": job_id})

    def update_job_status(self, job_id: str, status: str, notes: str = "") -> bool:
        """Update job status."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["jobs"]
        result = collection.update_one(
            {"_id": job_id},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.utcnow(),
                },
                "$push": {"notes": {"text": notes, "timestamp": datetime.utcnow()}}
                if notes
                else {},
            },
        )
        return result.modified_count > 0

    # Inventory Collection Operations
    def get_inventory_levels(self, low_stock_threshold: int = 10) -> List[Dict[str, Any]]:
        """Get current inventory levels, optionally filtered by low stock."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["inventory"]
        
        query = {}
        if low_stock_threshold:
            query["quantity"] = {"$lte": low_stock_threshold}
        
        return list(collection.find(query).sort("quantity", 1))

    def get_part_by_sku(self, sku: str) -> Optional[Dict[str, Any]]:
        """Get inventory item by SKU."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["inventory"]
        return collection.find_one({"sku": sku})

    def update_inventory_quantity(
        self, sku: str, quantity_change: int, reason: str = ""
    ) -> bool:
        """Update inventory quantity (positive for restock, negative for usage)."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["inventory"]
        result = collection.update_one(
            {"sku": sku},
            {
                "$inc": {"quantity": quantity_change},
                "$set": {"last_updated": datetime.utcnow()},
                "$push": {
                    "history": {
                        "change": quantity_change,
                        "reason": reason,
                        "timestamp": datetime.utcnow(),
                    }
                },
            },
        )
        return result.modified_count > 0

    def get_parts_for_job_type(self, job_type: str) -> List[Dict[str, Any]]:
        """Get commonly used parts for a specific job type."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["job_templates"]
        template = collection.find_one({"job_type": job_type})
        
        if not template or "required_parts" not in template:
            return []
        
        # Get actual inventory for these parts
        inventory_collection: Collection = self.db["inventory"]
        skus = [part["sku"] for part in template["required_parts"]]
        
        return list(inventory_collection.find({"sku": {"$in": skus}}))

    # Customers Collection Operations
    def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["customers"]
        return collection.find_one({"_id": customer_id})

    def get_overdue_invoices(self, days_overdue: int = 30) -> List[Dict[str, Any]]:
        """Get invoices overdue by specified days."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["invoices"]
        cutoff = datetime.utcnow() - timedelta(days=days_overdue)
        
        return list(
            collection.find(
                {
                    "status": {"$in": ["sent", "overdue"]},
                    "due_date": {"$lte": cutoff},
                    "paid_date": None,
                }
            ).sort("due_date", 1)
        )

    def update_invoice_status(
        self, invoice_id: str, status: str, paid_date: Optional[datetime] = None
    ) -> bool:
        """Update invoice status."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["invoices"]
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow(),
        }
        if paid_date:
            update_data["paid_date"] = paid_date
        
        result = collection.update_one(
            {"_id": invoice_id}, {"$set": update_data}
        )
        return result.modified_count > 0

    # Technicians Collection Operations
    def get_available_technicians(
        self, date: datetime, skills_required: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Get technicians available on a specific date with required skills."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["technicians"]
        
        query = {
            "active": True,
            "schedule": {
                "$not": {
                    "$elemMatch": {
                        "date": date.date().isoformat(),
                        "status": {"$in": ["unavailable", "vacation"]},
                    }
                }
            },
        }
        
        if skills_required:
            query["skills"] = {"$all": skills_required}
        
        return list(collection.find(query))

    def get_technician_schedule(
        self, tech_id: str, start_date: datetime, end_date: datetime
    ) -> List[Dict[str, Any]]:
        """Get technician's schedule for date range."""
        if not self.db:
            self.connect()
        
        collection: Collection = self.db["jobs"]
        return list(
            collection.find(
                {
                    "assigned_technician": tech_id,
                    "scheduled_date": {
                        "$gte": start_date,
                        "$lte": end_date,
                    },
                }
            ).sort("scheduled_date", 1)
        )


# Singleton instance for easy import
mongodb_tools = MongoDBTools()
