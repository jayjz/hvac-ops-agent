# utils/engine.py
import asyncio
import json
from uuid import uuid4
from typing import Any, Dict, List
import streamlit as st

from core.orchestrator import run_pm_job
from core.tools.mongodb_tools import mongodb_tools

class PMRunError(RuntimeError):
    def __init__(self, message: str, *, partial_result: dict[str, Any] | None, trace: list[str]) -> None:
        super().__init__(message)
        self.partial_result = partial_result
        self.trace = trace

def execute_pm_run(
    project_path: str | None,
    goals: List[str],
    live_mongo: bool,
) -> Dict[str, Any] | None:
    """Controller logic for executing the multi-agent PM run."""
    st.markdown('<div class="glass-card" style="padding: 1.5rem; margin-top: 1rem;">', unsafe_allow_html=True)
    
    with st.spinner("Initializing AgentForge Orchestrator..."):
        with st.status("Deploying PM agent team...", expanded=True) as status:
            progress = st.progress(0, text="Queued.")
            try:
                if live_mongo:
                    result = _run_job_with_live_progress(project_path, goals, progress, status)
                    result["data_source"] = {
                        "mode": "live_mongo",
                        "label": "Live Mongo",
                        "fallback": False,
                        "message": "MongoDB preflight passed; real orchestrator data path used.",
                    }
                else:
                    # Synthetic Fallback Route
                    result = _build_synthetic_result(goals, "Synthetic mode selected.")
                    progress.progress(1.0, text="Synthetic HVAC baseline ready.")
                    status.write("Done: Synthetic HVAC baseline ready.")
            except Exception as exc:
                status.update(label="AgentForge PM failed.", state="error", expanded=True)
                st.exception(exc)
                st.markdown("</div>", unsafe_allow_html=True)
                return None
            
            status.update(label="AgentForge PM complete.", state="complete", expanded=False)
            
    st.markdown("</div>", unsafe_allow_html=True)
    st.toast("AgentForge PM report is ready.", icon="✅")
    return result

def _run_job_with_live_progress(project_path: str | None, goals: List[str], progress: Any, status: Any) -> Dict[str, Any]:
    """Async wrapper for the orchestrator, hooked into Streamlit's progress bar."""
    job_id = f"streamlit-pm-{uuid4().hex[:10]}"
    trace: List[str] = []
    
    # We use a mutable dict to pass state between the async worker and the UI thread
    class JobState:
        def __init__(self):
            self.status = "PENDING"
            self.progress = 0.0
            self.details = "Queued."
            self.result = None
            
    jobs = {job_id: JobState()}

    async def runner() -> Dict[str, Any]:
        task = asyncio.create_task(
            run_pm_job(
                job_id=job_id,
                goals=goals,
                project_path=project_path,
                jobs=jobs,
            )
        )
        last_detail = ""
        while not task.done():
            job = jobs[job_id]
            detail = job.details or "Working."
            progress.progress(min(float(job.progress), 1.0), text=detail)
            if detail != last_detail:
                status.write(f"Done: {detail}")
                trace.append(detail)
                last_detail = detail
            await asyncio.sleep(0.35)

        job = jobs[job_id]
        try:
            result = await task
        except Exception as exc:
            raise PMRunError(str(exc), partial_result=job.result, trace=trace) from exc
            
        progress.progress(min(float(job.progress), 1.0), text=job.details)
        result["agent_trace"] = trace
        return result

    return asyncio.run(runner())

def _build_synthetic_result(goals: List[str], reason: str) -> Dict[str, Any]:
    """Provides a safe, static dataset when Mongo is disabled."""
    return {
        "execution_plan": [
            {"agent": "inventory_forecaster", "task": "Build synthetic baseline."},
            {"agent": "risk_assessor", "task": "Rank synthetic delivery risks."},
        ],
        "optimized_schedule": {
            "method": "synthetic",
            "duration_days": 47,
            "critical_path": ["Requirements validation", "Procurement", "Installation", "Commissioning"],
            "tasks": [
                {"task": "Requirements validation", "start_day": 0, "finish_day": 5, "duration_days": 5},
                {"task": "Procurement", "start_day": 5, "finish_day": 25, "duration_days": 20},
            ],
        },
        "pm_report": {
            "summary": "Synthetic PM baseline generated successfully.",
            "planned_duration_days": 47
        },
        "requirements_register": [
            {"id": "REQ-001", "domain": "HVAC", "priority": "High", "statement": goals[0] if goals else "Demo Goal"}
        ],
        "risk_register": [
            {"risk": "Long-lead equipment delay", "severity": "High", "score": 0.85, "mitigation": "Order now."}
        ],
        "overdue_invoices": [
            {"invoice_id": "INV-001", "customer_name": "Demo Corp", "amount": 1500.0, "days_overdue": 45}
        ],
        "data_source": {"mode": "synthetic", "label": "Synthetic fallback", "message": reason},
    }
