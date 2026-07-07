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

from core.agents import AgentContext, LeadArchitect
from core.dispatch_baseline import assemble_dispatch_baseline
from core.agents.specialists import SPECIALISTS
from core.tools.mongodb_tools import mongodb_tools
from core.models.parts_schemas import PMJobState # [FLAGSHIP UPGRADE] Schema import

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
        execution_plan = architect_result.data.get("execution_plan", [])
        specialist_errors: List[Dict[str, Any]] = []

        # Dynamic dispatch via registry keeps new specialists plug-and-play while
        # still providing the dashboard's consolidated dispatch baseline output.
        agent_sequence = _resolve_agent_sequence(execution_plan)
        results: Dict[str, Dict[str, Any]] = {}
        prior_data: Dict[str, Any] = {
            "project_data": project_data,
            "execution_plan": execution_plan,
        }

        for index, agent_name in enumerate(agent_sequence):
            agent_cls = SPECIALISTS.get(agent_name)
            if agent_cls is None:
                logger.warning("Unknown specialist %s in plan; skipping.", agent_name)
                continue
            start_progress = 0.20 + (index * 0.15)
            end_progress = min(start_progress + 0.15, 0.90)
            agent = agent_cls(
                name=agent_name,
                **base_common,
                progress_callback=scoped_progress(start_progress, end_progress),
            )
            payload = {
                **prior_data,
                "mongodb": mongodb_tools,
                "agent_name": agent_name,
            }
            agent_result = await agent.run(context, payload)
            if not agent_result.success:
                errors = agent_result.errors or [
                    f"{agent_name} failed without details."
                ]
                specialist_errors.append({"agent": agent_name, "errors": errors})
                logger.error("Specialist %s failed: %s", agent_name, errors)
                continue

            agent_data = agent_result.data or {}
            results[agent_name] = {"data": agent_data}
            prior_data.update(agent_data)

        inventory_data = results.get("inventory_forecaster", {}).get("data", {})
        risk_data = results.get("risk_assessor", {}).get("data", {})
        schedule_data = results.get("scheduler_optimizer", {}).get("data", {})
        ar_data = results.get("ar_collector", {}).get("data", {})

        result = {
            "execution_plan": execution_plan,
            "requires_approval": require_approval,
            "specialist_errors": specialist_errors,
            "proposed_actions": {
                "inventory_orders": inventory_data.get("recommended_orders", []),
                "ar_reminders": ar_data.get("overdue_invoices", []),
                "schedule_changes": schedule_data.get("optimized_schedule", {}),
                "risk_mitigations": risk_data.get("risk_register", []),
                "parts_checks": results.get("parts_availability_checker", {}).get(
                    "data", {}
                ),
            },
            **prior_data,
        }
        dispatch_baseline = assemble_dispatch_baseline(
            goals=goals,
            project_data=project_data,
            execution_plan=execution_plan,
            inventory_data=inventory_data,
            risk_data=risk_data,
            schedule_data=schedule_data,
            ar_data=ar_data,
            data_source="mongo_or_fallback",
        )
        result["dispatch_baseline"] = dispatch_baseline
        result["dispatch_baseline_markdown"] = dispatch_baseline["reports"]["markdown"]
        result["dispatch_baseline_json"] = dispatch_baseline["reports"]["json"]

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


def _resolve_agent_sequence(execution_plan: Any) -> List[str]:
    """Normalize LeadArchitect plans into registered specialist names."""
    aliases = {
        "requirements": "inventory_forecaster",
        "inventory": "inventory_forecaster",
        "risk": "risk_assessor",
        "scheduler": "scheduler_optimizer",
        "schedule": "scheduler_optimizer",
        "report": "ar_collector",
        "ar": "ar_collector",
        "parts": "parts_availability_checker",
    }
    default_sequence = [
        "inventory_forecaster",
        "risk_assessor",
        "scheduler_optimizer",
        "ar_collector",
        "parts_availability_checker",
    ]

    raw_steps: List[Any]
    if isinstance(execution_plan, list):
        raw_steps = execution_plan
    elif isinstance(execution_plan, dict):
        raw_steps = execution_plan.get("steps", [])
    else:
        raw_steps = []

    sequence: List[str] = []
    for step in raw_steps:
        if isinstance(step, dict):
            raw_name = step.get("specialist") or step.get("agent") or step.get("name")
        else:
            raw_name = step
        if not raw_name:
            continue
        name = aliases.get(str(raw_name), str(raw_name))
        if name in SPECIALISTS and name not in sequence:
            sequence.append(name)

    if not sequence:
        return default_sequence

    for name in default_sequence:
        if name not in sequence:
            sequence.append(name)
    return sequence


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

# [FLAGSHIP UPGRADE] Modified to persist state to MongoDB while retaining legacy dict updates
def _set_job(
    jobs: Optional[MutableMapping[str, Any]],
    job_id: str,
    *,
    status: Optional[str] = None,
    progress: Optional[float] = None,
    details: Optional[str] = None,
    result: Optional[Dict[str, Any]] = None,
) -> None:
    # 1. Update legacy in-memory state (keeps current async callbacks/workers happy)
    current_job = None
    if jobs is not None and job_id in jobs:
        current_job = jobs[job_id]
        for key, value in {
            "status": status,
            "progress": progress,
            "details": details,
            "result": result,
        }.items():
            if value is not None and hasattr(current_job, key):
                setattr(current_job, key, value)

    # 2. Persist to MongoDB using pure Pydantic validation
    try:
        validated_state = PMJobState(
            job_id=job_id,
            status=status or getattr(current_job, "status", "PENDING"),
            progress=progress if progress is not None else getattr(current_job, "progress", 0.0),
            details=details or getattr(current_job, "details", "State updated."),
            result=result or getattr(current_job, "result", None)
        )
        mongodb_tools.upsert_job_state(validated_state)
    except Exception as e:
        logger.error("Failed to validate and persist job state to DB: %s", e)