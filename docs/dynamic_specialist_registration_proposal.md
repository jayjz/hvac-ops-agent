# Proposal: Dynamic Specialist Registration in Orchestrator (Do Not Implement Yet)

## Current Problem
- Orchestrator uses hardcoded sequential execution of specialists.
- Adding new agents (e.g. JobCloseoutAgent, PredictiveReorderingAgent) requires manual edits to orchestrator.py and lead_architect.py.
- Violates Open/Closed Principle in clean architecture.

## Proposed Solution (for future implementation after approval)
1. In core/agents/specialists.py or a new registry.py:
   ```python
   from core.agents.base import BaseAgent
   SPECIALISTS = {}

   def register_specialist(name: str):
       def decorator(cls):
           if issubclass(cls, BaseAgent):
               SPECIALISTS[name] = cls
           return cls
       return decorator
   ```

2. Decorate each specialist:
   ```python
   @register_specialist("parts_availability_checker")
   class PartsAvailabilityCheckerAgent(BaseAgent):
       ...
   ```

3. In core/orchestrator.py (dynamic):
   ```python
   from core.agents.specialists import SPECIALISTS
   class Orchestrator:
       def __init__(self):
           self.specialists = SPECIALISTS
       
       async def execute_plan(self, plan, context, payload):
           for step in plan.get("steps", []):
               specialist_name = step["agent"]
               if specialist_name in self.specialists:
                   agent_class = self.specialists[specialist_name]
                   agent = agent_class()
                   result = await agent.execute(context, {**payload, "step": step})
                   ...
   ```

4. Lead Architect can query available specialists via registry for dynamic planning.

## Benefits
- Automatic registration on import.
- Easy to add new specialists without touching orchestrator.
- Supports clean architecture (interfaces via BaseAgent).
- Scalable for full HVAC roster (InventoryForecaster, ARFollowUp, etc.).

**Status**: Proposal only. Do not edit orchestrator.py until explicit user approval and new TDD tests written first (per TDD skill and PROJECT_MEMORY.md).

Created: 2026-06-05
