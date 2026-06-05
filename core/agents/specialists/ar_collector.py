"""Individual specialist file post-split."""

from ..base import BaseAgent
from . import register_specialist


@register_specialist("ar_collector")
class ARCollectorAgent(BaseAgent):
    pass
