"""TDD tests for PartsAvailabilityCheckerAgent (Refactor phase).
Strict adherence to test-driven-development skill: watched failures, minimal Green fixes, refactor for coverage >80%.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from core.agents.specialists import PartsAvailabilityCheckerAgent
from core.models import AgentResult, RequiredPart


@pytest.mark.asyncio
async def test_all_parts_in_stock():
    """Happy path."""
    mock_mongodb = MagicMock()
    mock_mongodb.get_low_inventory.return_value = []

    agent = PartsAvailabilityCheckerAgent(name="parts_availability_checker")
    context = MagicMock()
    agent.report_progress = AsyncMock()

    required_parts = [RequiredPart(sku="HP-001", name="Heat Pump Unit", quantity=1)]

    result: AgentResult = await agent.execute(
        context=context,
        payload={
            "mongodb": mock_mongodb,
            "job_id": "job-full-stock-001",
            "required_parts": required_parts,
        },
    )

    assert result.success is True
    assert result.agent == "parts_availability_checker"
    data = result.data
    assert data["all_parts_available"] is True
    assert data["availability_score"] == 1.0
    assert len(data.get("reorder_recommendations", [])) == 0
    assert "All parts in stock" in data.get("summary", "")
    agent.report_progress.assert_called()


@pytest.mark.asyncio
async def test_flags_missing_parts_and_recommends_reorder():
    """Shortfall with reorder and urgency."""
    mock_mongodb = MagicMock()
    mock_mongodb.get_low_inventory.return_value = [
        {"sku": "FILTER-01", "quantity": 5, "name": "Air Filter"}
    ]

    agent = PartsAvailabilityCheckerAgent(name="parts_availability_checker")
    context = MagicMock()
    agent.report_progress = AsyncMock()

    required_parts = [RequiredPart(sku="FILTER-01", name="Air Filter", quantity=12)]

    result: AgentResult = await agent.execute(
        context=context,
        payload={
            "mongodb": mock_mongodb,
            "job_id": "job-shortfall-002",
            "required_parts": required_parts,
        },
    )

    assert result.success is True
    data = result.data
    assert not data["all_parts_available"]
    assert data["availability_score"] < 0.8
    assert len(data.get("reorder_recommendations", [])) > 0
    rec = data["reorder_recommendations"][0]
    assert rec["sku"] == "FILTER-01"
    assert rec["urgency"] in ("medium", "high")
    assert rec.get("recommended_quantity", 0) > 0
    agent.report_progress.assert_called()


@pytest.mark.parametrize(
    "test_case,required_parts,low_inventory,expected_available,expected_score,expected_reorder_count,expected_urgency",
    [
        ("no_parts", [], [], True, 1.0, 0, None),
        (
            "zero_stock",
            [RequiredPart(sku="PUMP-001", name="Main Pump", quantity=5)],
            [{"sku": "PUMP-001", "quantity": 0}],
            False,
            0.0,
            1,
            "high",
        ),
        (
            "partial",
            [RequiredPart(sku="BELT-01", name="Drive Belt", quantity=3)],
            [{"sku": "BELT-01", "quantity": 1}],
            False,
            0.33,
            1,
            "high",
        ),
        (
            "high_shortfall",
            [RequiredPart(sku="COMP-01", name="Compressor", quantity=10)],
            [{"sku": "COMP-01", "quantity": 1}],
            False,
            0.1,
            1,
            "high",
        ),
    ],
)
@pytest.mark.asyncio
async def test_edge_cases(
    test_case,
    required_parts,
    low_inventory,
    expected_available,
    expected_score,
    expected_reorder_count,
    expected_urgency,
):
    """Parametrized edge cases for >80% coverage (no_parts, stock levels, urgency variants, exception paths)."""
    mock_mongodb = MagicMock()
    mock_mongodb.get_low_inventory.return_value = low_inventory

    agent = PartsAvailabilityCheckerAgent(name="parts_availability_checker")
    context = MagicMock()
    agent.report_progress = AsyncMock()
    agent.logger = MagicMock()

    result: AgentResult = await agent.execute(
        context=context,
        payload={
            "mongodb": mock_mongodb,
            "job_id": f"job-{test_case}-001",
            "required_parts": required_parts,
        },
    )

    assert result.success is True
    data = result.data
    assert data["all_parts_available"] is expected_available
    assert abs(data["availability_score"] - expected_score) < 0.05
    assert len(data.get("reorder_recommendations", [])) == expected_reorder_count
    if expected_reorder_count > 0 and expected_urgency:
        recs = data.get("reorder_recommendations", [])
        assert recs[0]["urgency"] == expected_urgency
    agent.report_progress.assert_called()


@pytest.mark.asyncio
async def test_exception_handling():
    """Exception path coverage."""
    mock_mongodb = MagicMock()
    mock_mongodb.get_low_inventory.side_effect = Exception("MongoDB timeout")

    agent = PartsAvailabilityCheckerAgent(name="parts_availability_checker")
    context = MagicMock()
    agent.report_progress = AsyncMock()
    agent.logger = MagicMock()

    result: AgentResult = await agent.execute(
        context=context,
        payload={
            "mongodb": mock_mongodb,
            "job_id": "job-exception-001",
            "required_parts": [
                RequiredPart(sku="TEST-01", name="Test Part", quantity=2)
            ],
        },
    )

    assert result.success is True
    agent.logger.warning.assert_called()
    agent.report_progress.assert_called()
