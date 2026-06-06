"""Specialists package with dynamic registry for HVAC agents.
Registry enables Phase 1 dynamic orchestrator. Split supports scalable maintenance.
Ruff cleaned and verified 2026-06-06. Circular import fixed by placing specialist imports AFTER decorator with noqa: E402.
"""

from __future__ import annotations

from typing import Dict, Type

from core.agents.base import BaseAgent

# === DYNAMIC SPECIALIST REGISTRY ===
SPECIALISTS: Dict[str, Type[BaseAgent]] = {}


def register_specialist(name: str):
    """Decorator for dynamic registration. Orchestrator lookups by name.
    Supports auto-discovery, clean architecture, and Streamlit dashboard integration.
    """

    def decorator(cls: Type[BaseAgent]) -> Type[BaseAgent]:
        if issubclass(cls, BaseAgent):
            SPECIALISTS[name] = cls
            if not hasattr(cls, "name") or not cls.name:
                setattr(cls, "name", name)
        return cls

    return decorator


# Import all specialist implementations (triggers @register_specialist decorators)
# Placed AFTER decorator to avoid circular import during package initialization
from .ar_collector import ARCollectorAgent  # noqa: E402
from .inventory_forecaster import InventoryForecasterAgent  # noqa: E402
from .parts_availability_checker import PartsAvailabilityCheckerAgent  # noqa: E402
from .risk_assessor import RiskAssessorAgent  # noqa: E402
from .scheduler_optimizer import SchedulerOptimizerAgent  # noqa: E402

__all__ = [
    "SPECIALISTS",
    "register_specialist",
    "InventoryForecasterAgent",
    "RiskAssessorAgent",
    "SchedulerOptimizerAgent",
    "ARCollectorAgent",
    "PartsAvailabilityCheckerAgent",
]
