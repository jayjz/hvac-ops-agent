"""Pydantic schemas for PartsAvailabilityChecker (Phase 3 grounding + legacy compatibility).
Schemas first per clean architecture, TDD, and hvac-refactor-phase.md.
Combines new models with previous for backward compat.
JTBD: Structured real-time parts data for Mongo-grounded dashboard, reduces wasted trips by 30-50%.
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
    "AgentResult",
]
