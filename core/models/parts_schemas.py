"""Pydantic schemas for PartsAvailabilityChecker and ARCollector (Phase 3+6 grounding + legacy compatibility).
Schemas first per clean architecture, TDD skill, hvac-refactor-phase.md, and PROJECT_MEMORY.md canonical Business VP.
Now includes Invoice/ARResult for full JTBD loop (parts availability + AR/cashflow for proactive HVAC ops, 30-50% less downtime).
Canonical VP from PROJECT_MEMORY.md: HVAC OpsForge as AI Co-Pilot; JTBD (functional: real-time validated parts/AR data to avoid delays/multiple trips; emotional: peace of mind on cashflow; social: competitive edge); Porter's Five Forces (supplier power reduced by predictive reorders, rivalry lowered by dashboard speed/visibility, buyer power managed by reliable summaries, substitutes (Excel/ServiceTitan) countered by schema-AI/registry moat, new entrants barrier via proprietary validation); scholarly PdM 38-91% downtime cuts, multi-agent systems, computational intelligence, JTBD framework; quantified 30-50% less downtime/more billable, 25% inventory optimization, faster AR/cashflow.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime


class ReorderRecommendation(BaseModel):
    """Recommendation for reordering specific part."""
    sku: str = Field(..., description="Part SKU")
    suggested_quantity: int = Field(..., gt=0, description="Recommended reorder qty")
    reason: str = Field(..., description="Low stock, lead time, etc.")
    estimated_cost: Optional[float] = Field(None, ge=0, description="Projected cost")
    priority: str = Field("medium", pattern="^(high|medium|low)$")


class JobPartsRequest(BaseModel):
    """Input for parts availability check (new)."""
    job_id: str = Field(..., min_length=3)
    job_type: str
    required_parts: List[str] = Field(..., min_length=1)
    urgency_level: str = Field("medium", pattern="^(high|medium|low)$")
    customer_id: Optional[str] = None
    scheduled_date: Optional[datetime] = None

    @field_validator("required_parts")
    @classmethod
    def validate_parts(cls, v: List[str]) -> List[str]:
        if not v or len(v) == 0:
            raise ValueError("At least one part required")
        return [p.upper().strip() for p in v]


class PartsAvailabilityResult(BaseModel):
    """Output with score, recommendations, Mongo sync status."""
    job_id: str
    availability_score: float = Field(..., ge=0, le=1.0)
    recommendations: List[ReorderRecommendation] = Field(default_factory=list)
    mongo_synced: bool = False
    estimated_downtime_reduction: Optional[float] = Field(None, ge=0)
    message: str = "Availability checked via registry + MongoDB"
    timestamp: datetime = Field(default_factory=datetime.now)

    @field_validator("availability_score")
    @classmethod
    def round_score(cls, v: float) -> float:
        return round(float(v), 2)


# Legacy compatibility for existing __init__ and tests (Phase 2/1)
class RequiredPart(BaseModel):
    sku: str
    name: Optional[str] = None
    quantity: int = 1


class PartsAvailabilityRequest(JobPartsRequest):
    """Alias for backward compat."""
    pass


class PartCheckResult(PartsAvailabilityResult):
    """Alias."""
    pass


class InventoryItem(BaseModel):
    """Pydantic model for validated inventory records from MongoDB (Phase 4 hardening)."""
    sku: str = Field(..., min_length=3)
    name: str
    quantity: int = Field(..., ge=0)
    reorder_point: int = Field(..., ge=0)
    unit_cost: float = Field(..., ge=0)
    category: Optional[str] = Field("general", description="equipment/consumable/refrigerant")


class JobDocument(BaseModel):
    """Pydantic model for validated job records from MongoDB."""
    job_id: str
    job_type: str
    customer_name: str
    scheduled_date: datetime
    status: str = Field(..., pattern=r"^(scheduled|confirmed|in_progress|completed)$")
    estimated_hours: Optional[int] = Field(None, ge=0)
    customer_id: Optional[str] = None
    urgency: Optional[str] = "medium"


# Phase 6 ARCollector models for full JTBD loop (AR follow-ups, cashflow scoring combined with Parts)
class Invoice(BaseModel):
    """Pydantic model for validated AR invoices from Mongo (Phase 6)."""
    invoice_id: str = Field(..., min_length=5)
    amount: float = Field(..., gt=0)
    due_date: datetime
    status: str = Field("pending", pattern=r"^(paid|overdue|pending)$")
    customer_id: str
    days_overdue: Optional[int] = Field(0, ge=0)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        return v.lower()


class ARResult(BaseModel):
    """AR + Parts combined result for full JTBD cashflow/availability loop (cites PROJECT_MEMORY.md VP)."""
    cashflow_score: float = Field(..., ge=0, le=1.0)
    overdue_count: int = Field(..., ge=0)
    total_overdue_amount: float = Field(..., ge=0)
    recommendations: List[str] = Field(default_factory=list)
    mongo_synced: bool = False
    combined_parts_availability_score: Optional[float] = None
    message: str = "AR follow-up with cashflow scoring via validated Mongo + Parts integration per canonical VP"
    timestamp: datetime = Field(default_factory=datetime.now)

    @field_validator("cashflow_score")
    @classmethod
    def round_score(cls, v: float) -> float:
        return round(float(v), 2)


class AgentResult(BaseModel):
    """Simple result wrapper for compatibility."""
    success: bool = True
    data: Dict[str, Any] = Field(default_factory=dict)
    agent: str = "parts_availability_checker"


__all__ = [
    "JobPartsRequest",
    "PartsAvailabilityResult",
    "ReorderRecommendation",
    "RequiredPart",
    "PartsAvailabilityRequest",
    "PartCheckResult",
    "InventoryItem",
    "JobDocument",
    "Invoice",
    "ARResult",
    "AgentResult",
]
