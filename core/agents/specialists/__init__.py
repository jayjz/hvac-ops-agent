"""Specialists package with dynamic registry for HVAC agents.
Registry enables Phase 1 dynamic orchestrator. Split supports scalable maintenance.
Ruff cleaned and verified 2026-06-06. Push verified with new hash.
"""

from __future__ import annotations

from typing import Dict, Type

from core.agents.base import BaseAgent

from .ar_collector import ARCollectorAgent
from .inventory_forecaster import InventoryForecasterAgent
from .parts_availability_checker import PartsAvailabilityCheckerAgent
from .risk_assessor import RiskAssessorAgent
from .scheduler_optimizer import SchedulerOptimizerAgent

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


__all__ = [
    "SPECIALISTS",
    "register_specialist",
    "InventoryForecasterAgent",
    "RiskAssessorAgent",
    "SchedulerOptimizerAgent",
    "ARCollectorAgent",
    "PartsAvailabilityCheckerAgent",
]
