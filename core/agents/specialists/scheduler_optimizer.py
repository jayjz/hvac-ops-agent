"""Individual specialist file post-split."""

from ..base import BaseAgent
from . import register_specialist


@register_specialist("scheduler_optimizer")
class SchedulerOptimizerAgent(BaseAgent):
    pass
