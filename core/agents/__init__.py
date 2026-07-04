"""HVAC OpsForge agent package."""

from core.agents.base import AgentContext, AgentResult, BaseAgent, ProgressCallback
from core.agents.lead_architect import LeadArchitect
from core.agents.specialists import (
    ARCollectorAgent,
    InventoryForecasterAgent,
    RiskAssessorAgent,
    SchedulerOptimizerAgent,
)

__all__ = [
    "AgentContext",
    "AgentResult",
    "BaseAgent",
    "LeadArchitect",
    "ProgressCallback",
    "ARCollectorAgent",
    "InventoryForecasterAgent",
    "RiskAssessorAgent",
    "SchedulerOptimizerAgent",
]

# Dynamic registry for orchestrator (added for clean architecture and demo scalability)
from core.agents.specialists import SPECIALISTS, register_specialist

__all__ += ["SPECIALISTS", "register_specialist"]
