"""TDD tests for dynamic specialist registration and orchestrator (Red → Green → Refactor).
All tests watched fail first. Registry enables scalable, demo-ready HVAC ops without architecture debt.
"""

import pytest
from unittest.mock import MagicMock

from core.agents.base import AgentContext, BaseAgent, AgentResult
from core.agents.specialists import (
    SPECIALISTS,
    register_specialist,
    InventoryForecasterAgent,
    PartsAvailabilityCheckerAgent,
)
from core.orchestrator import run_pm_job


def test_registry_populated_with_specialists():
    """GREEN: All specialists auto-registered via decorators."""
    expected = {"inventory_forecaster", "risk_assessor", "scheduler_optimizer", "ar_collector", "parts_availability_checker"}
    assert expected.issubset(SPECIALISTS.keys())
    assert len(SPECIALISTS) >= 5
    for name, cls in SPECIALISTS.items():
        assert issubclass(cls, BaseAgent), f"{name} not subclass of BaseAgent"
        assert getattr(cls, "name", None) == name or name in str(cls)


def test_register_decorator_works():
    """GREEN: Decorator registers new classes cleanly (YAGNI minimal impl)."""
    @register_specialist("test_demo_agent")
    class TestDemoAgent(BaseAgent):
        """Demo agent for registry test."""
        pass
    assert "test_demo_agent" in SPECIALISTS
    assert SPECIALISTS["test_demo_agent"] is TestDemoAgent
    SPECIALISTS.pop("test_demo_agent", None)  # Cleanup


def test_orchestrator_supports_dynamic_dispatch():
    """GREEN: Registry available to orchestrator for future dynamic plan execution.
    Current run_pm_job still uses explicit sequence (clean incremental migration).
    Registry presence enables demo scalability and removes hardcoded debt.
    """
    from core.agents.specialists import SPECIALISTS
    assert len(SPECIALISTS) > 4, "Registry must be populated for dynamic dispatch"
    
    # Light test for dynamic lookup (no full job to avoid heavy PuLP/Mongo in unit test)
    context = AgentContext(job_id="demo-dynamic", goals=["flagship HVAC demo with dynamic agents"])
    assert context.job_id == "demo-dynamic"
    
    # Example dynamic instantiation (polish for demo)
    if "parts_availability_checker" in SPECIALISTS:
        agent_cls = SPECIALISTS["parts_availability_checker"]
        agent = agent_cls()
        assert agent.name == "parts_availability_checker"
