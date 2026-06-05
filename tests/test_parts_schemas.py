"""TDD RED-GREEN for Phase 3: Pydantic schemas for PartsAvailabilityChecker + Mongo grounding.
RED phase first: import fails, validation errors expected before implementation.
JTBD: Real-time parts availability with structured data for dashboard and reordering.
"""
import pytest
from pydantic import ValidationError
from unittest.mock import patch, MagicMock
from core.agents.specialists.parts_availability_checker import PartsAvailabilityCheckerAgent
from core.models.parts_schemas import (
    JobPartsRequest,
    PartsAvailabilityResult,
    ReorderRecommendation,
)
from core.tools.mongodb_tools import mongodb_tools


def test_parts_schemas_validation():
    """RED: Should fail until models implemented. Then test valid/invalid data."""
    # This will fail on import first (RED)
    valid_request = JobPartsRequest(
        job_id="job-123",
        job_type="ac_repair",
        required_parts=["HP-001", "FILTER-01"],
        urgency_level="medium",
    )
    assert valid_request.job_id == "job-123"
    assert len(valid_request.required_parts) == 2

    # Invalid should raise
    with pytest.raises(ValidationError):
        JobPartsRequest(job_id="bad", required_parts=[])


def test_parts_availability_result():
    """RED/GREEN: Result model with score, recommendations, Mongo-backed data."""
    result = PartsAvailabilityResult(
        job_id="job-123",
        availability_score=0.92,
        recommendations=[ReorderRecommendation(sku="HP-001", suggested_quantity=2, reason="low_stock")],
        mongo_synced=True,
    )
    assert result.availability_score > 0.8
    assert len(result.recommendations) == 1


@pytest.mark.asyncio
async def test_parts_availability_checker_with_schemas():
    """RED first: Test agent uses schemas + Mongo tools. Watch for missing impl."""
    context = MagicMock()
    request = JobPartsRequest(
        job_id="demo-job",
        job_type="maintenance",
        required_parts=["FILTER-01"],
    )
    agent = PartsAvailabilityCheckerAgent()
    result = await agent.execute(context, request.model_dump())

    assert result.success
    assert "availability_score" in result.data
    assert isinstance(result.data.get("availability_score"), float)
    # Mongo integration test (synthetic OK for live)
    with patch.object(mongodb_tools, "get_low_inventory") as mock_low:
        mock_low.return_value = [{"sku": "FILTER-01", "quantity": 5}]
        # Re-test with real tool
        pass  # GREEN after agent update


def test_mongodb_parts_query_integration():
    """RED: Test new Mongo methods for stock check."""
    # Expect new method or enhanced get_low_inventory
    low = mongodb_tools.get_low_inventory(threshold_multiplier=1.0)
    assert len(low) > 0
    assert any(hasattr(item, "sku") or "sku" in str(item) for item in low)


if __name__ == "__main__":
    pytest.main([__file__, "-q", "--asyncio-mode=auto"])
