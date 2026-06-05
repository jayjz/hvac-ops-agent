from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

# Full schemas for HVAC OpsForge (Phase 3+ normalization + Phase 9 pure Pydantic). All validators, legacy aliases, docstrings with verbatim canonical VP/JTBD/Porter's from PROJECT_MEMORY.md single source of truth. Used by mongodb_tools (all reads return validated models), agents, tests, Streamlit, Scheduler.

class ReorderRecommendation(BaseModel):
    sku: str
    suggested_quantity: int = Field(ge=1)
    reason: str
    estimated_cost: float = Field(ge=0)
    priority: str = Field(pattern=r'^(high|medium|low)$')

    @field_validator('sku')
    @classmethod
    def uppercase_sku(cls, v: str) -> str:
        return v.upper()

class JobPartsRequest(BaseModel):
    job_id: str
    job_type: str
    required_parts: List[str] = Field(min_length=1)

    @field_validator('required_parts')
    @classmethod
    def uppercase_parts(cls, v: List[str]) -> List[str]:
        return [p.upper() for p in v]

class PartsAvailabilityResult(BaseModel):
    availability_score: float = Field(ge=0, le=1)
    recommendations: List[ReorderRecommendation] = Field(default_factory=list)
    mongo_synced: bool = False
    estimated_downtime_reduction: float = Field(ge=0, le=1)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @field_validator('availability_score', 'estimated_downtime_reduction')
    @classmethod
    def round_scores(cls, v: float) -> float:
        return round(v, 2)

class InventoryItem(BaseModel):
    sku: str
    name: str
    quantity: int = Field(ge=0)
    reorder_point: int = Field(ge=0)
    unit_cost: float = Field(ge=0)
    category: str

class JobDocument(BaseModel):
    job_id: str
    job_type: str
    customer_name: str
    scheduled_date: str
    status: str = Field(pattern=r'^(scheduled|confirmed|in_progress|completed)$')
    estimated_hours: float = Field(ge=0)
    customer_id: Optional[str] = None
    urgency: Optional[float] = None

class Invoice(BaseModel):
    invoice_id: str
    customer_name: str
    amount: float = Field(ge=0)
    days_overdue: int = Field(ge=0)
    status: str = Field(pattern=r'^(sent|overdue|pending|paid)$')

class ARResult(BaseModel):
    cashflow_score: float = Field(ge=0, le=1)
    overdue_count: int = Field(ge=0)
    total_overdue_amount: float = Field(ge=0)
    recommendations: List[str] = Field(default_factory=list)
    mongo_synced: bool = False
    combined_parts_availability_score: float = Field(ge=0, le=1)
    message: str = Field(default="AR per PROJECT_MEMORY.md canonical VP")

    @field_validator('cashflow_score', 'combined_parts_availability_score')
    @classmethod
    def round_scores(cls, v: float) -> float:
        return round(v, 2)

class ScheduleOptimizationResult(BaseModel):
    """Pydantic model for SchedulerOptimizer. Canonical VP from PROJECT_MEMORY.md single source of truth (full text): HVAC OpsForge Agent is the AI Operations Co-Pilot that turns reactive small-trades chaos into proactive, first-visit efficiency. For owners/techs: \"When planning or starting a daily job, get validated real-time parts availability, smart reorders, and risk flags from your Mongo data — so you finish jobs faster, cut downtime 30-50%, optimize inventory 25%, and improve cashflow without spreadsheets or guesswork.\" JTBD Core: Functional (parts on truck, jobs completed), emotional (peace of mind), social (competitive edge). Porter's Five Forces Edge (HVAC): Supplier Power reduced via predictive reordering; Rivalry lowered by dashboard speed; Buyer Power managed through retention; Substitutes countered by schema-enforced AI vs Excel/ServiceTitan; New Entrants barrier via proprietary registry + validation moat. Scholarly: PdM cuts unplanned failures 38-91%, multi-agent systems, computational intelligence, JTBD framework. Metrics embedded in all results."""
    optimized_jobs: List[str] = Field(default_factory=list)
    route_efficiency_score: float = Field(..., ge=0, le=1)
    estimated_downtime_reduction: float = Field(..., ge=0, le=1)
    message: str = Field(default="Optimized per PROJECT_MEMORY.md canonical VP/JTBD/Porter's - 30-50% less downtime")
    mongo_synced: bool = True

    @field_validator("route_efficiency_score", "estimated_downtime_reduction")
    @classmethod
    def round_scores(cls, v: float) -> float:
        return round(v, 2)

# Legacy aliases for backward compatibility (Phase 3+)
PartsAvailabilityRequest = JobPartsRequest
PartCheckResult = PartsAvailabilityResult
RequiredPart = ReorderRecommendation
# AR and Scheduler models already canonical

__all__ = [
    "JobPartsRequest", "PartsAvailabilityResult", "ReorderRecommendation",
    "InventoryItem", "JobDocument", "Invoice", "ARResult", "ScheduleOptimizationResult",
    "PartsAvailabilityRequest", "PartCheckResult", "RequiredPart"
]
