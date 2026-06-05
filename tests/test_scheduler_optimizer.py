import pytest
from unittest.mock import AsyncMock, MagicMock
from core.models.parts_schemas import ScheduleOptimizationResult, PartsAvailabilityResult, ARResult, JobDocument, InventoryItem, Invoice
from core.agents.specialists.scheduler_optimizer import SchedulerOptimizerAgent
from core.tools.mongodb_tools import mongodb_tools

@pytest.mark.asyncio
async def test_scheduler_optimizer_combines_parts_ar_and_produces_valid_route():
    context = MagicMock()
    context.job_id = "test-job-001"
    context.progress_callback = AsyncMock()
    agent = SchedulerOptimizerAgent()
    
    # Use real Pydantic models for normalization test (RED phase for hybrid removal)
    parts_result = PartsAvailabilityResult(
        availability_score=0.85,
        recommendations=[],
        mongo_synced=True,
        estimated_downtime_reduction=0.42
    )
    ar_result = ARResult(
        cashflow_score=0.78,
        overdue_count=3,
        total_overdue_amount=7100.0,
        recommendations=[],
        mongo_synced=True,
        combined_parts_availability_score=0.82,
        message="AR per PROJECT_MEMORY.md"
    )
    
    result = await agent.execute(context, parts_result=parts_result, ar_result=ar_result, use_live_mongo=True)
    
    assert isinstance(result, ScheduleOptimizationResult)
    assert result.mongo_synced is True
    assert 0.0 <= result.route_efficiency_score <= 1.0
    assert len(result.optimized_jobs) > 0
    assert result.estimated_downtime_reduction > 0.3
    assert "canonical VP from PROJECT_MEMORY.md" in result.message.lower()
    # New for Phase 9 deepened route + pure Pydantic
    assert any("JOB" in str(job).upper() for job in result.optimized_jobs)
    assert "route_efficiency" in result.model_dump()

@pytest.mark.asyncio
async def test_mongodb_tools_returns_pure_pydantic_no_hybrids():
    # RED for normalization: expects only Pydantic models, no dict or getattr in paths
    jobs = mongodb_tools.get_upcoming_jobs()
    low_inventory = mongodb_tools.get_low_inventory(1.5)
    overdue = mongodb_tools.get_overdue_invoices()
    assert all(isinstance(j, JobDocument) for j in jobs)
    assert all(isinstance(item, InventoryItem) for item in low_inventory)
    assert all(isinstance(inv, Invoice) for inv in overdue)  # will fail until normalized
    # No hybrid code path exercised
    assert not any(hasattr(item, 'get') for item in low_inventory)  # pure models
