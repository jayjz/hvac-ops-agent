"""Individual specialist file post-split."""

from ..base import BaseAgent
from . import register_specialist


@register_specialist("risk_assessor")
class RiskAssessorAgent(BaseAgent):
    pass
