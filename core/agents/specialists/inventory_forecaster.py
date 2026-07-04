"""Individual specialist file post-split."""

from ..base import BaseAgent
from . import register_specialist


@register_specialist("inventory_forecaster")
class InventoryForecasterAgent(BaseAgent):
    pass
