"""Specialists package with dynamic registry for HVAC agents.
Registry enables Phase 1 dynamic orchestrator (b230b4a). Split supports scalable maintenance.
"""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from core.agents.base import AgentContext, AgentResult, BaseAgent

# === DYNAMIC SPECIALIST REGISTRY (moved from monolithic for Phase 2) ===
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


# Import all specialist implementations (GREEN after individual files created)
from .inventory_forecaster import InventoryForecasterAgent
from .risk_assessor import RiskAssessorAgent
from .scheduler_optimizer import SchedulerOptimizerAgent
from .ar_collector import ARCollectorAgent
from .parts_availability_checker import PartsAvailabilityCheckerAgent

__all__ = [
    "SPECIALISTS",
    "register_specialist",
    "InventoryForecasterAgent",
    "RiskAssessorAgent",
    "SchedulerOptimizerAgent",
    "ARCollectorAgent",
    "PartsAvailabilityCheckerAgent",
]
