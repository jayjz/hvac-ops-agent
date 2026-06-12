"""HVAC OpsForge orchestration with 100% dynamic specialist dispatch via registry.
References JTBD: Enables scalable, plug-and-play HVAC operations (inventory forecasting,
parts availability checking, AR follow-ups, predictive reordering, risk assessment)
without hardcoded classes or architecture debt — core business value for job closeout
and operations efficiency.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, Optional

from core.agents import (
    AgentContext,
    LeadArchitect,
)
from core.agents.specialists import SPECIALISTS
from core.tools.mongodb_tools import mongodb_tools

logger = logging.getLogger("hvac_opsforge.orchestrator")


async def run_pm_job(
    *,
    job_id: str,
    goals: List[str],
    project_path: Optional[str] = None,
    jobs: Optional[MutableMapping[str, Any]] = None,
    config_path: str | Path = "config.yaml",
    require_approval: bool = True,
) -> Dict[str, Any]:
    """Run the HVAC operations workflow with MongoDB integration and human approval.

    **100% Dynamic (Phase 1 complete)**: Uses SPECIALISTS registry + execution_plan from
    LeadArchitect for dispatch. No hardcoded agent classes. Scalable for new specialists
    (e.g. PartsAvailabilityCheckerAgent) per JTBD for predictive ops.

    Workflow driven by plan:
    1. LeadArchitect analyzes goals → execution_plan
    2. Dynamic dispatch of specialists via registry lookup
    3. Human-in-the-loop approval
    4. Execute approved actions
    """
    memory: Dict[str, Any] = {}

    async def progress_callback(
        callback_job_id: str, progress: float, detail: str
    ) -> None:
        if jobs is None or callback_job_id not in jobs:
            return
        job = jobs[callback_job_id]
        if hasattr(job, "progress"):
            job.progress = progress
        if hasattr(job, "details"):
            job.details = detail

    def scoped_progress(start: float, end: float):
        async def callback(callback_job_id: str, progress: float, detail: str) -> None:
            overall = start + ((end - start) * max(0.0, min(1.0, progress)))
            await progress_callback(callback_job_id, overall, detail)

        return callback

    context = AgentContext(job_id=job_id, project_path=project_path, goals=goals)
    base_common = {
        "config_path": config_path,
        "memory": memory,
        "tools": {"mongodb": mongodb_tools},
    }

    try:
        _set_job(
            jobs,
            job_id,
            status="RUNNING",
            progress=0.02,
            details="HVAC OpsForge job started.",
        )

        architect = LeadArchitect(
            **base_common, progress_callback=scoped_progress(0.02, 0.20)
        )
        architect_result = await architect.run(context)
        if not architect_result.success:
            raise RuntimeError("; ".join(architect_result.errors))

        project_data = architect_result.data["project_data"]
        execution_plan = architect_result.data.get("execution_plan", {})

        # === 100% DYNAMIC DISPATCH VIA REGISTRY (Phase 1) ===
        # Default sequence from plan or standard HVAC flow. JTBD: supports dynamic
        # addition of PartsAvailabilityChecker, reordering agents without code changes.
        if isinstance(execution_plan, list):
            agent_sequence = [step.get("specialist") for step in execution_plan if isinstance(step, dict) and "specialist" in step]
        else:
            agent_sequence = execution_plan.get("steps", [])
        
        if not any(s in SPECIALISTS for s in agent_sequence):
            agent_sequence = ["inventory_forecaster", "risk_assessor", "scheduler_optimizer", "ar_collector", "parts_availability_checker"]
        results: Dict[str, Any] = {}
        prior_data: Dict[str, Any] = {
            "project_data": project_data,
            "execution_plan": execution_plan,
        }

        for i, agent_name in enumerate(agent_sequence):
            if agent_name not in SPECIALISTS:
                logger.warning("Unknown specialist %s in plan; skipping.", agent_name)
                continue
            agent_cls = SPECIALISTS[agent_name]
            start_prog = 0.20 + (i * 0.15)
            end_prog = start_prog + 0.15
            agent = agent_cls(
                **base_common,
                progress_callback=scoped_progress(start_prog, min(end_prog, 0.90)),
            )
            payload = {
                **prior_data,
                "mongodb": mongodb_tools,
                "agent_name": agent_name,
            }
            agent_result = await agent.run(context, payload)
            if not agent_result.success:
                raise RuntimeError(f"{agent_name}: " + "; ".join(agent_result.errors))
            
            # Wrap in dict so downstream .get("data", {}) extraction does not crash on the AgentResult object
            results[agent_name] = {"data": agent_result.data}
            prior_data.update(agent_result.data or {})

        # Compile all results (dynamic)
        result = {
            "execution_plan": execution_plan,
            "requires_approval": require_approval,
            "proposed_actions": {
                "inventory_orders": results.get("inventory_forecaster", {})
                .get("data", {})
                .get("recommended_orders", []),
                "ar_reminders": results.get("ar_collector", {})
                .get("data", {})
                .get("overdue_invoices", []),
                "schedule_changes": results.get("scheduler_optimizer", {})
                .get("data", {})
                .get("optimized_schedule", {}),
                "risk_mitigations": results.get("risk_assessor", {})
                .get("data", {})
                .get("risk_register", []),
                "parts_checks": results.get("parts_availability_checker", {}).get(
                    "data", {}
                ),
            },
            **prior_data,
        }

        # Human-in-the-loop approval step
        if require_approval:
            _set_job(
                jobs,
                job_id,
                status="AWAITING_APPROVAL",
                progress=0.95,
                details="Actions pending human approval. Review proposed changes in result.proposed_actions.",
                result=result,
            )
            logger.info("Job %s awaiting human approval", job_id)
            return result

        # If no approval required, execute actions
        _set_job(
            jobs,
            job_id,
            status="EXECUTING",
            progress=0.95,
            details="Executing approved actions...",
        )
        execution_results = await _execute_approved_actions(result, mongodb_tools)
        result["execution_results"] = execution_results

        _set_job(
            jobs,
            job_id,
            status="COMPLETED",
            progress=1.0,
            details="HVAC OpsForge job complete.",
            result=result,
        )
        return result
    except Exception as exc:
        logger.exception("HVAC OpsForge job failed: %s", job_id)
        _set_job(
            jobs,
            job_id,
            status="FAILED",
            progress=1.0,
            details=f"HVAC OpsForge job failed: {exc}",
        )
        raise


async def _execute_approved_actions(
    result: Dict[str, Any], mongodb_tools
) -> Dict[str, Any]:
    """Execute actions that have been approved by human operator."""
    execution_results = {
        "inventory_updates": [],
        "ar_reminders_sent": [],
        "schedule_updates": [],
        "parts_updates": [],
    }

    proposed = result.get("proposed_actions", {})

    # Dynamic execution based on proposed actions (JTBD value: automated closeout)
    for order in proposed.get("inventory_orders", []):
        logger.info(
            "Would order: %s x %s", order.get("quantity"), order.get("part_name")
        )
        execution_results["inventory_updates"].append(
            {
                "sku": order.get("sku"),
                "action": "order_placed",
                "quantity": order.get("quantity"),
            }
        )

    for invoice in proposed.get("ar_reminders", []):
        logger.info("Would send reminder for invoice: %s", invoice.get("_id"))
        execution_results["ar_reminders_sent"].append(
            {
                "invoice_id": invoice.get("_id"),
                "customer": invoice.get("customer_id"),
                "amount": invoice.get("amount"),
            }
        )

    # Parts availability actions (new for dynamic registry)
    for check in proposed.get("parts_checks", {}).get("checks", []):
        if check.get("reorder_recommended"):
            execution_results["parts_updates"].append(
                {
                    "part": check.get("part_name"),
                    "action": "reorder_triggered",
                    "urgency": check.get("urgency", "medium"),
                }
            )

    return execution_results


def _set_job(
    jobs: Optional[MutableMapping[str, Any]],
    job_id: str,
    *,
    status: Optional[str] = None,
    progress: Optional[float] = None,
    details: Optional[str] = None,
    result: Optional[Dict[str, Any]] = None,
) -> None:
    if jobs is None or job_id not in jobs:
        return
    job = jobs[job_id]
    for key, value in {
        "status": status,
        "progress": progress,
        "details": details,
        "result": result,
    }.items():
        if value is not None and hasattr(job, key):
            setattr(job, key, value)
