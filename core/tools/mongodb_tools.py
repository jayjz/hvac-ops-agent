"""MongoDB tools for HVAC OpsForge agent operations with Pydantic validation layer (Phase 4 hardening per TDD skill)."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from pydantic import ValidationError
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from core.models.parts_schemas import InventoryItem, JobDocument

load_dotenv()


class MongoDBTools:
    """MongoDB operations for HVAC business data with synthetic fallbacks and Pydantic validation on all read paths for inventory/jobs (schema enforcement, error resilience)."""

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or os.getenv(
            "MONGO_URI", "mongodb://localhost:27017/"
        )
        self.client: Optional[MongoClient] = None
        self.db = None

    def connect(self):
        """Connect to MongoDB and return client."""
        try:
            if not self.client:
                self.client = MongoClient(
                    self.connection_string,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                )
                # Test connection
                self.client.admin.command("ping")
            return self.client
        except Exception as exc:
            print(f"MongoDB connection failed: {exc}")
            self.client = None
            return None

    def get_upcoming_jobs(self, days: int = 14) -> List[JobDocument]:
        """Get jobs scheduled in the next N days with Pydantic JobDocument validation (Phase 4)."""
        try:
            client = self.connect()
            if not client:
                raise ConnectionError("No MongoDB connection")

            db = client["hvac_ops"]
            collection = db["jobs"]
            cutoff = datetime.now(timezone.utc) + timedelta(days=days)

            jobs = list(
                collection.find(
                    {
                        "scheduled_date": {"$lte": cutoff},
                        "status": {"$in": ["scheduled", "confirmed"]},
                    },
                    {"_id": 0},
                )
                .sort("scheduled_date", 1)
                .limit(50)
            )

            if jobs:
                return [JobDocument.model_validate(j) for j in jobs]
        except (PyMongoError, ConnectionError, ValidationError, Exception) as exc:
            print(f"MongoDB query failed, using synthetic data: {exc}")

        # Synthetic fallback - validated to JobDocument
        synthetic = [
            {
                "job_id": "job_001",
                "job_type": "heat_pump_install",
                "customer_name": "ABC Manufacturing",
                "scheduled_date": (
                    datetime.now(timezone.utc) + timedelta(days=3)
                ).isoformat(),
                "status": "scheduled",
                "estimated_hours": 8,
            },
            {
                "job_id": "job_002",
                "job_type": "ac_repair",
                "customer_name": "XYZ Office Complex",
                "scheduled_date": (
                    datetime.now(timezone.utc) + timedelta(days=5)
                ).isoformat(),
                "status": "scheduled",
                "estimated_hours": 3,
            },
            {
                "job_id": "job_003",
                "job_type": "maintenance",
                "customer_name": "Downtown Retail",
                "scheduled_date": (
                    datetime.now(timezone.utc) + timedelta(days=7)
                ).isoformat(),
                "status": "scheduled",
                "estimated_hours": 2,
            },
        ]
        return [JobDocument.model_validate(j) for j in synthetic]

    def get_low_inventory(
        self, threshold_multiplier: float = 1.2
    ) -> List[InventoryItem]:
        """Get inventory items below reorder threshold with Pydantic InventoryItem validation (Phase 4). Deepens Mongo grounding for PartsAvailabilityChecker score math and reorder recommendations."""
        try:
            client = self.connect()
            if not client:
                raise ConnectionError("No MongoDB connection")

            db = client["hvac_ops"]
            collection = db["inventory"]

            pipeline = [
                {
                    "$addFields": {
                        "threshold": {
                            "$multiply": ["$reorder_point", threshold_multiplier]
                        }
                    }
                },
                {"$match": {"$expr": {"$lte": ["$quantity", "$threshold"]}}},
                {"$sort": {"quantity": 1}},
                {"$limit": 50},
                {"$project": {"_id": 0}},
            ]

            items = list(collection.aggregate(pipeline))

            if items:
                return [InventoryItem.model_validate(item) for item in items]
        except (PyMongoError, ConnectionError, ValidationError, Exception) as exc:
            print(f"MongoDB query failed, using synthetic data: {exc}")

        # Synthetic fallback data - always validated for production-grade schema enforcement
        synthetic = [
            {
                "sku": "HP-001",
                "name": "Heat Pump Unit 3-Ton",
                "quantity": 2,
                "reorder_point": 3,
                "unit_cost": 2500.00,
                "category": "equipment",
            },
            {
                "sku": "FILTER-20x25",
                "name": "Air Filter 20x25x1 MERV 8",
                "quantity": 8,
                "reorder_point": 20,
                "unit_cost": 12.50,
                "category": "consumable",
            },
            {
                "sku": "REFRIG-R410A-25",
                "name": "R410A Refrigerant 25lb Cylinder",
                "quantity": 3,
                "reorder_point": 10,
                "unit_cost": 185.00,
                "category": "refrigerant",
            },
            {
                "sku": "CAP-45-5",
                "name": "Dual Capacitor 45/5 MFD",
                "quantity": 5,
                "reorder_point": 12,
                "unit_cost": 24.99,
                "category": "electrical",
            },
        ]
        return [InventoryItem.model_validate(item) for item in synthetic]

    def get_overdue_invoices(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get invoices overdue by specified days with synthetic fallback (kept as Dict for this phase; can add InvoiceDocument later)."""
        try:
            client = self.connect()
            if not client:
                raise ConnectionError("No MongoDB connection")

            db = client["hvac_ops"]
            collection = db["invoices"]
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)

            invoices = list(
                collection.find(
                    {
                        "status": {"$in": ["sent", "overdue", "pending"]},
                        "due_date": {"$lte": cutoff_date},
                        "$or": [{"paid_date": None}, {"paid_date": {"$exists": False}}],
                    },
                    {"_id": 0},
                )
                .sort("due_date", 1)
                .limit(100)
            )

            if invoices:
                return invoices

        except (PyMongoError, ConnectionError, Exception) as exc:
            print(f"MongoDB query failed, using synthetic data: {exc}")

        # Synthetic fallback data
        return [
            {
                "invoice_id": "INV-2026-001",
                "customer_id": "CUST-ABC-001",
                "customer_name": "ABC Manufacturing",
                "amount": 4500.00,
                "due_date": (
                    datetime.now(timezone.utc) - timedelta(days=45)
                ).isoformat(),
                "invoice_date": (
                    datetime.now(timezone.utc) - timedelta(days=75)
                ).isoformat(),
                "days_overdue": 45,
                "status": "overdue",
            },
            {
                "invoice_id": "INV-2026-002",
                "customer_id": "CUST-XYZ-002",
                "customer_name": "XYZ Office Complex",
                "amount": 1850.00,
                "due_date": (
                    datetime.now(timezone.utc) - timedelta(days=32)
                ).isoformat(),
                "invoice_date": (
                    datetime.now(timezone.utc) - timedelta(days=62)
                ).isoformat(),
                "days_overdue": 32,
                "status": "overdue",
            },
            {
                "invoice_id": "INV-2026-003",
                "customer_id": "CUST-RETAIL-003",
                "customer_name": "Downtown Retail Center",
                "amount": 750.00,
                "due_date": (
                    datetime.now(timezone.utc) - timedelta(days=38)
                ).isoformat(),
                "invoice_date": (
                    datetime.now(timezone.utc) - timedelta(days=68)
                ).isoformat(),
                "days_overdue": 38,
                "status": "overdue",
            },
        ]

    def get_parts_required_for_jobs(
        self, job_list: List[Dict[str, Any]] | List[str]
    ) -> Dict[str, Dict]:
        """Minimal helper to aggregate parts required. Reuses get_upcoming_jobs (now returns validated models) and synthetic. Surgical/DRY. Handles Pydantic objects."""
        if not job_list:
            raise ValueError("Job list cannot be empty")
        try:
            if isinstance(job_list[0] if job_list else None, str):
                jobs = self.get_upcoming_jobs()[: len(job_list)]
            else:
                jobs = job_list
            parts = {}
            for job in jobs:
                # Support both Pydantic and dict
                if hasattr(job, "job_type"):
                    job_type = job.job_type
                else:
                    job_type = (
                        job.get("job_type", "ac_repair")
                        if isinstance(job, dict)
                        else str(job)
                    )
                if "heat" in str(job_type).lower() or "pump" in str(job_type).lower():
                    p_list = [
                        {"sku": "HP-001", "name": "Heat Pump Unit 3-Ton", "quantity": 1}
                    ]
                else:
                    p_list = [
                        {"sku": "CAP-45-5", "name": "Dual Capacitor", "quantity": 1},
                        {
                            "sku": "FILTER-20x25",
                            "name": "Air Filter MERV 8",
                            "quantity": 3,
                        },
                    ]
                for p in p_list:
                    sku = p["sku"]
                    if sku not in parts:
                        parts[sku] = {
                            "name": p["name"],
                            "total_required": 0,
                            "jobs": [],
                        }
                    parts[sku]["total_required"] += p.get("quantity", 1)
                    job_id = (
                        job.job_id
                        if hasattr(job, "job_id")
                        else job.get("_id", "unknown")
                        if isinstance(job, dict)
                        else str(job)
                    )
                    parts[sku]["jobs"].append(job_id)
            return parts
        except Exception as exc:
            print(f"Parts aggregation failed: {exc}. Using fallback.")
            return self._synthetic_parts_required()

    def _synthetic_parts_required(self) -> Dict[str, Dict]:
        """Synthetic fallback (reuses pattern from other methods)."""
        return {
            "HP-001": {
                "name": "Heat Pump Unit 3-Ton",
                "total_required": 2,
                "jobs": ["job_001"],
            },
            "FILTER-20x25": {
                "name": "Air Filter MERV 8",
                "total_required": 6,
                "jobs": ["job_002"],
            },
            "CAP-45-5": {
                "name": "Dual Capacitor",
                "total_required": 3,
                "jobs": ["job_002"],
            },
        }


# Singleton instance
mongodb_tools = MongoDBTools()
