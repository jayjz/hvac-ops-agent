"""HVAC OpsForge orchestration."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, MutableMapping, Optional

from core.agents import (
    AgentContext,
    AgentResult,
    LeadArchitect,
    ARCollectorAgent,
    InventoryForecasterAgent,
    RiskAssessorAgent,
    SchedulerOptimizerAgent,
)
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
    
    Workflow:
    1. LeadArchitect analyzes goals and creates execution plan
    2. InventoryForecasterAgent analyzes upcoming jobs and checks stock levels via MongoDB
    3. RiskAssessorAgent identifies operational risks (low stock, overdue AR, scheduling conflicts)
    4. SchedulerOptimizerAgent optimizes technician assignments using MongoDB data
    5. ARCollectorAgent identifies overdue invoices from MongoDB
    6. Human-in-the-loop approval before executing actions
    7. Execute approved actions (update inventory, send reminders, etc.)
    """

    memory: Dict[str, Any] = {}

    async def progress_callback(callback_job_id: str, progress: float, detail: str) -> None:
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
    # Add MongoDB tools to agent context
    base_common = {
        "config_path": config_path, 
        "memory": memory,
        "tools": {"mongodb": mongodb_tools}
    }

    try:
        _set_job(jobs, job_id, status="RUNNING", progress=0.02, details="HVAC OpsForge job started.")

        architect = LeadArchitect(**base_common, progress_callback=scoped_progress(0.02, 0.20))
        architect_result = await architect.run(context)
        if not architect_result.success:
            raise RuntimeError("; ".join(architect_result.errors))

        project_data = architect_result.data["project_data"]
        execution_plan = architect_result.data["execution_plan"]
        specialist_errors: List[Dict[str, Any]] = []

        async def run_specialist(
            agent,
            payload: Dict[str, Any],
            fallback_data: Dict[str, Any],
        ) -> AgentResult:
            try:
                result = await agent.run(context, payload)
            except Exception as exc:
                logger.exception("Specialist %s raised unexpectedly", agent.name)
                result = AgentResult(agent=agent.name, success=False, errors=[str(exc)])
            if result.success:
                return result
            errors = result.errors or [f"{agent.name} failed without details."]
            logger.error(
                "Specialist %s failed; continuing with fallback data: %s",
                agent.name,
                errors,
            )
            specialist_errors.append({"agent": agent.name, "errors": errors})
            return AgentResult(
                agent=agent.name,
                success=False,
                data=fallback_data,
                errors=errors,
                warnings=["Fallback data used so the demo workflow could continue."],
            )

        # Step 1: Inventory forecasting with MongoDB integration
        inventory = InventoryForecasterAgent(**base_common, progress_callback=scoped_progress(0.20, 0.40))
        inventory_result = await run_specialist(
            inventory,
            {
                "project_data": project_data,
                "execution_plan": execution_plan,
                "mongodb": mongodb_tools,
            },
            {
                "requirements_register": [],
                "inventory_forecast": {},
                "recommended_orders": [],
                "upcoming_jobs_count": 0,
                "low_stock_items": 0,
            },
        )

        # Step 2: Risk assessment using MongoDB data
        risk = RiskAssessorAgent(**base_common, progress_callback=scoped_progress(0.40, 0.60))
        risk_result = await run_specialist(
            risk,
            {
                **inventory_result.data,
                "project_data": project_data,
                "mongodb": mongodb_tools,
            },
            {"risk_register": []},
        )

        # Step 3: Schedule optimization with technician data from MongoDB
        scheduler = SchedulerOptimizerAgent(**base_common, progress_callback=scoped_progress(0.60, 0.75))
        schedule_result = await run_specialist(
            scheduler,
            {
                **inventory_result.data,
                **risk_result.data,
                "project_data": project_data,
                "mongodb": mongodb_tools,
            },
            {
                "optimized_schedule": {
                    "method": "fallback",
                    "duration_days": None,
                    "tasks": [],
                    "critical_path": [],
                }
            },
        )

        # Step 4: AR collection using MongoDB invoices
        ar_collector = ARCollectorAgent(**base_common, progress_callback=scoped_progress(0.75, 0.90))
        ar_result = await run_specialist(
            ar_collector,
            {
                **inventory_result.data,
                **risk_result.data,
                **schedule_result.data,
                "mongodb": mongodb_tools,
            },
            {
                "pm_report": {
                    "summary": "AR collector unavailable; workflow continued with remaining specialist outputs.",
                    "requirements_count": len(
                        inventory_result.data.get("requirements_register", [])
                    ),
                    "high_risk_count": len(
                        [
                            risk
                            for risk in risk_result.data.get("risk_register", [])
                            if risk.get("severity") == "High"
                        ]
                    ),
                    "planned_duration_days": schedule_result.data.get(
                        "optimized_schedule", {}
                    ).get("duration_days"),
                    "critical_path": schedule_result.data.get(
                        "optimized_schedule", {}
                    ).get("critical_path", []),
                    "ar_summary": {
                        "overdue_count": 0,
                        "total_amount": 0,
                        "oldest_invoice_days": 0,
                    },
                    "recommended_actions": [
                        "Review AR collector logs before sending invoice reminders."
                    ],
                    "risk_chart_path": None,
                },
                "overdue_invoices": [],
                "total_overdue_amount": 0,
                "invoices_count": 0,
            },
        )

        # Compile all results
        result = {
            "execution_plan": execution_plan,
            "requires_approval": require_approval,
            "specialist_errors": specialist_errors,
            "proposed_actions": {
                "inventory_orders": inventory_result.data.get("recommended_orders", []),
                "ar_reminders": ar_result.data.get("overdue_invoices", []),
                "schedule_changes": schedule_result.data.get("optimized_schedule", {}),
                "risk_mitigations": risk_result.data.get("risk_register", []),
            },
            **inventory_result.data,
            **risk_result.data,
            **schedule_result.data,
            **ar_result.data,
        }

        # Human-in-the-loop approval step
        if require_approval:
            _set_job(
                jobs, 
                job_id, 
                status="AWAITING_APPROVAL", 
                progress=0.95, 
                details="Actions pending human approval. Review proposed changes in result.proposed_actions.",
                result=result
            )
            logger.info("Job %s awaiting human approval", job_id)
            # In a real implementation, this would pause and wait for approval
            # For now, we mark as awaiting approval and return
            return result
        
        # If no approval required, execute actions
        _set_job(jobs, job_id, status="EXECUTING", progress=0.95, details="Executing approved actions...")
        
        # Execute the approved actions (in production, this would be gated by approval)
        execution_results = await _execute_approved_actions(result, mongodb_tools)
        result["execution_results"] = execution_results

        _set_job(jobs, job_id, status="COMPLETED", progress=1.0, details="HVAC OpsForge job complete.", result=result)
        return result
    except Exception as exc:
        logger.exception("HVAC OpsForge job failed: %s", job_id)
        _set_job(jobs, job_id, status="FAILED", progress=1.0, details=f"HVAC OpsForge job failed: {exc}")
        raise


async def _execute_approved_actions(result: Dict[str, Any], mongodb_tools) -> Dict[str, Any]:
    """Execute actions that have been approved by human operator."""
    execution_results = {
        "inventory_updates": [],
        "ar_reminders_sent": [],
        "schedule_updates": [],
    }
    
    # Example: Update inventory based on recommendations
    # In production, this would actually execute the MongoDB updates
    # For demo, we just log what would happen
    
    proposed = result.get("proposed_actions", {})
    
    # Log inventory actions (would update MongoDB in production)
    for order in proposed.get("inventory_orders", []):
        logger.info("Would order: %s x %s", order.get("quantity"), order.get("part_name"))
        execution_results["inventory_updates"].append({
            "sku": order.get("sku"),
            "action": "order_placed",
            "quantity": order.get("quantity"),
        })
    
    # Log AR actions (would send emails in production)
    for invoice in proposed.get("ar_reminders", []):
        logger.info("Would send reminder for invoice: %s", invoice.get("_id"))
        execution_results["ar_reminders_sent"].append({
            "invoice_id": invoice.get("_id"),
            "customer": invoice.get("customer_id"),
            "amount": invoice.get("amount"),
        })
    
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
    for key, value in {"status": status, "progress": progress, "details": details, "result": result}.items():
        if value is not None and hasattr(job, key):
            setattr(job, key, value)
