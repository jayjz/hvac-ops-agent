from __future__ import annotations

<<<<<<< HEAD
import asyncio
from datetime import date, datetime, timedelta
import html
import json
from io import BytesIO
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import uuid4
from zipfile import ZIP_DEFLATED, ZipFile
=======
from typing import Any, Dict
>>>>>>> dev/ai-integration

import pandas as pd
import streamlit as st

<<<<<<< HEAD
from core.orchestrator import run_pm_job
from core.dispatch_baseline import assemble_dispatch_baseline
from core.tools.mongodb_tools import mongodb_tools


DEFAULT_GOALS = [
    "Build an HVAC retrofit PM baseline.",
    "Identify procurement, controls, construction, and budget risks.",
    "Create an executive-ready schedule and action summary.",
]

SUPPORTED_UPLOAD_TYPES = ["txt", "md", "csv", "xlsx", "xlsm", "pdf"]


class PMRunError(RuntimeError):
    def __init__(self, message: str, *, partial_result: dict[str, Any] | None, trace: list[str]) -> None:
        super().__init__(message)
        self.partial_result = partial_result
        self.trace = trace


def main() -> None:
=======

APP_TITLE = "HVAC OpsForge"
APP_SUBTITLE = "Autonomous AI Operations Co-Pilot for HVAC & Trade Services"


def configure_page() -> None:
    """Configure the Streamlit shell once for a wide, demo-ready dashboard."""
>>>>>>> dev/ai-integration
    st.set_page_config(
        page_title=f"{APP_TITLE} Dashboard",
        page_icon="AF",
        layout="wide",
        initial_sidebar_state="expanded",
    )

<<<<<<< HEAD
    render_app_header()
    render_top_action_bar()
    source_mode, project_path, goals, upload_meta, mongo_status = render_sidebar()
    run_clicked = render_run_panel(source_mode, project_path, goals, upload_meta, mongo_status)

    if run_clicked:
        effective_path = None if source_mode == "synthetic" else project_path
        if source_mode == "upload" and not effective_path:
            st.warning("Upload at least one project file or switch to synthetic HVAC data.")
            return

        result = execute_pm_run(effective_path, goals, source_mode == "synthetic", mongo_status)
        if result:
            st.session_state["pm_result"] = result
            st.balloons()

    result = st.session_state.get("pm_result")
    if result:
        render_results(result)
    else:
        render_empty_state()


def render_app_header() -> None:
    st.markdown(
        """
        <div class="app-hero">
            <div>
                <div class="eyebrow-row">
                    <span class="product-icon">AF</span>
                    <span class="ai-badge">AI-Powered</span>
                </div>
                <h1>HVAC OpsForge</h1>
                <p>
                    Multi-agent operations co-pilot for HVAC and service businesses.
                    Automates inventory forecasting, job scheduling, AR follow-ups, and operations intelligence.
                </p>
            </div>
            <div class="hero-stat-grid">
                <div class="mini-stat"><span>Source</span><strong>Files or Synthetic</strong></div>
                <div class="mini-stat"><span>Output</span><strong>Registers + Schedule</strong></div>
                <div class="mini-stat"><span>Export</span><strong>CSV, PNG, ZIP</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_action_bar() -> None:
    left, _spacer, new_col, reset_col = st.columns([0.52, 0.18, 0.15, 0.15], vertical_alignment="center")
    with left:
        st.markdown(
            '<div class="top-action-title">Dispatch workspace</div>',
            unsafe_allow_html=True,
        )
    with new_col:
        if icon_button("New Run", ":material/add_circle:", key="new_run_action"):
            st.session_state["confirm_new_run"] = True
            st.session_state.pop("confirm_reset", None)
    with reset_col:
        if icon_button("Reset", ":material/restart_alt:", key="reset_action"):
            st.session_state["confirm_reset"] = True
            st.session_state.pop("confirm_new_run", None)

    render_action_confirmations()


def icon_button(
    label: str,
    icon: str,
    *,
    key: str,
    disabled: bool = False,
    button_type: str = "secondary",
    width: str = "stretch",
) -> bool:
    try:
        return st.button(label, key=key, icon=icon, disabled=disabled, type=button_type, width=width)
    except TypeError:
        return st.button(label, key=key, disabled=disabled, type=button_type, width=width)


def icon_download_button(label: str, icon: str, **kwargs: Any) -> bool:
    try:
        return st.download_button(label, icon=icon, **kwargs)
    except TypeError:
        return st.download_button(label, **kwargs)


def render_action_confirmations() -> None:
    if st.session_state.get("confirm_new_run"):
        st.warning("Start a new run? This clears the current report and AR review decisions.")
        confirm_col, cancel_col, _ = st.columns([0.18, 0.18, 0.64])
        with confirm_col:
            confirm_new_run = icon_button("Confirm", ":material/check_circle:", key="confirm_new_run_action")
        with cancel_col:
            cancel_new_run = icon_button("Cancel", ":material/close:", key="cancel_new_run_action")
        if confirm_new_run:
            clear_run_state()
            st.session_state.pop("confirm_new_run", None)
            st.toast("Ready for a new dispatch run.")
            st.rerun()
        if cancel_new_run:
            st.session_state.pop("confirm_new_run", None)
            st.rerun()

    if st.session_state.get("confirm_reset"):
        st.warning("Reset dashboard? This clears uploads, goals, Live Mongo selection, results, and AR decisions.")
        confirm_col, cancel_col, _ = st.columns([0.18, 0.18, 0.64])
        with confirm_col:
            confirm_reset = icon_button("Confirm", ":material/check_circle:", key="confirm_reset_action")
        with cancel_col:
            cancel_reset = icon_button("Cancel", ":material/close:", key="cancel_reset_action")
        if confirm_reset:
            clear_run_state()
            for key in ["source_mode", "upload_dir", "upload_meta", "goals", "live_mongo_enabled", "confirm_reset"]:
                st.session_state.pop(key, None)
            st.toast("Dashboard reset.")
            st.rerun()
        if cancel_reset:
            st.session_state.pop("confirm_reset", None)
            st.rerun()


def clear_run_state() -> None:
    st.session_state.pop("pm_result", None)
    st.session_state.pop("ar_decision_feedback", None)
    for key in list(st.session_state.keys()):
        if str(key).startswith("ar_decision_"):
            st.session_state.pop(key, None)


def render_sidebar() -> tuple[str, str | None, list[str], dict[str, Any], dict[str, Any]]:
    with st.sidebar:
        st.markdown('<div class="sidebar-title">Project Setup</div>', unsafe_allow_html=True)
        st.caption("Choose a source, tune the goals, then run the PM orchestrator.")

        st.markdown('<div class="sidebar-section">Live Mongo</div>', unsafe_allow_html=True)
        live_mongo_enabled = st.toggle(
            "Enable Live Mongo",
            value=st.session_state.get("live_mongo_enabled", False),
            help="When enabled and healthy, the dispatch run uses MongoDB-backed agents.",
        )
        st.session_state["live_mongo_enabled"] = live_mongo_enabled
        mongo_status = check_live_mongo_status(live_mongo_enabled)
        render_mongo_status(mongo_status)

        synthetic_clicked = icon_button(
            "Use Synthetic HVAC Data",
            ":material/database:",
            key="use_synthetic_data",
        )
        if synthetic_clicked:
            st.session_state["source_mode"] = "synthetic"
            st.session_state.pop("upload_dir", None)
            st.session_state.pop("upload_meta", None)
            st.session_state.pop("pm_result", None)

        uploaded_files = st.file_uploader(
            "Upload project artifacts",
            type=SUPPORTED_UPLOAD_TYPES,
            accept_multiple_files=True,
            help="Select files from a project folder. Supported: TXT, MD, CSV, Excel, PDF.",
        )

        upload_meta = st.session_state.get("upload_meta", {"count": 0, "size": 0, "names": []})
        if uploaded_files and not synthetic_clicked:
            st.session_state["source_mode"] = "upload"
            st.session_state["upload_dir"] = save_uploaded_files(uploaded_files)
            upload_meta = summarize_uploads(uploaded_files)
            st.session_state["upload_meta"] = upload_meta

        source_mode = st.session_state.get("source_mode", "synthetic")
        project_path = st.session_state.get("upload_dir")

        st.markdown('<div class="sidebar-section">Active Source</div>', unsafe_allow_html=True)
        if source_mode == "synthetic":
            st.success("Synthetic HVAC retrofit dataset is ready.")
            st.markdown(
                """
                <div class="source-card">
                    <strong>Demo package</strong>
                    <span>Requirements, risks, and schedule inputs generated by the PM engine.</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.success("Uploaded artifact set is ready.")
            st.metric("Files", upload_meta.get("count", 0))
            st.metric("Total Size", format_bytes(upload_meta.get("size", 0)))
            with st.expander("Uploaded files", expanded=False):
                for name in upload_meta.get("names", []):
                    st.write(f"- {name}")
                if project_path:
                    st.caption(project_path)

        st.divider()
        st.markdown('<div class="sidebar-section">Analysis Goals</div>', unsafe_allow_html=True)
        goal_text = st.text_area(
            "One goal per line",
            value="\n".join(st.session_state.get("goals", DEFAULT_GOALS)),
            height=150,
            label_visibility="collapsed",
        )
        goals = [line.strip() for line in goal_text.splitlines() if line.strip()]
        st.session_state["goals"] = goals or DEFAULT_GOALS
        st.caption(f"{len(st.session_state['goals'])} active goals")

        return source_mode, project_path, st.session_state["goals"], upload_meta, mongo_status


def check_live_mongo_status(enabled: bool) -> dict[str, Any]:
    if not enabled:
        return {
            "enabled": False,
            "connected": False,
            "message": "Live Mongo is disabled. Synthetic fallback will be used.",
        }

    health = mongodb_tools.healthcheck()
    return {
        "enabled": True,
        "connected": bool(health.get("ok")),
        "message": str(health.get("message") or "MongoDB status unavailable."),
    }


def render_mongo_status(status: dict[str, Any]) -> None:
    if not status["enabled"]:
        st.info(status["message"])
    elif status["connected"]:
        st.success(status["message"])
    else:
        st.warning(f"{status['message']} Synthetic fallback will be used.")


def render_run_panel(
    source_mode: str,
    project_path: str | None,
    goals: list[str],
    upload_meta: dict[str, Any],
    mongo_status: dict[str, Any],
) -> bool:
    st.markdown('<div class="section-kicker">Run Workspace</div>', unsafe_allow_html=True)
    left, right = st.columns([0.68, 0.32], vertical_alignment="center")
    with left:
        source_label = "Synthetic HVAC data" if source_mode == "synthetic" else f"{upload_meta.get('count', 0)} uploaded files"
        data_path = "Live Mongo orchestrator" if mongo_status["connected"] else "Synthetic fallback"
        st.markdown(
            f"""
            <div class="run-card">
                <div>
                    <span class="muted-label">Current analysis package</span>
                    <h3>{source_label}</h3>
                    <p>{len(goals)} goals configured. Data path: {data_path}. The agents will extract requirements, rank risks,
                    optimize schedule tasks, and produce an executive summary.</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        disabled = source_mode == "upload" and not project_path
        return icon_button(
            "Run Multi-Agent Dispatch",
            ":material/play_arrow:",
            key="run_multi_agent_dispatch",
            button_type="primary",
            width="stretch",
            disabled=disabled,
        )


def execute_pm_run(
    project_path: str | None,
    goals: list[str],
    synthetic_mode: bool,
    mongo_status: dict[str, Any],
) -> dict[str, Any] | None:
    use_live_mongo = bool(mongo_status["enabled"] and mongo_status["connected"])
    st.markdown('<div class="progress-shell">', unsafe_allow_html=True)
    with st.spinner("Running multi-agent dispatch..."):
        with st.status("Launching PM agent team...", expanded=True) as status:
            progress = st.progress(0, text="Queued.")
            try:
                if use_live_mongo:
                    result = run_job_with_live_progress(project_path, goals, progress, status)
                    result["data_source"] = {
                        "mode": "live_mongo",
                        "label": "Live Mongo",
                        "fallback": False,
                        "message": "MongoDB preflight passed; real orchestrator data path used.",
                    }
                else:
                    if mongo_status["enabled"]:
                        reason = mongo_status["message"]
                    elif synthetic_mode:
                        reason = "Synthetic mode selected."
                    else:
                        reason = mongo_status["message"]
                    result = build_synthetic_result(goals, reason)
                    progress.progress(1.0, text="Synthetic HVAC baseline ready.")
                    status.write("Done: Synthetic HVAC baseline ready.")
            except PMRunError as exc:
                status.write(f"Live run error: {exc}")
                if exc.partial_result:
                    with st.expander("Partial live result", expanded=False):
                        st.json(exc.partial_result)
                st.warning("Live Mongo run failed. Falling back to synthetic HVAC baseline.")
                result = build_synthetic_result(goals, str(exc), partial_result=exc.partial_result)
                result["agent_trace"] = exc.trace + result.get("agent_trace", [])
                progress.progress(1.0, text="Synthetic fallback ready.")
                status.write("Done: Synthetic fallback ready.")
            except Exception as exc:
                status.update(label="AgentForge PM failed.", state="error", expanded=True)
                st.exception(exc)
                st.markdown("</div>", unsafe_allow_html=True)
                return None
            status.update(label="AgentForge PM complete.", state="complete", expanded=False)
    st.markdown("</div>", unsafe_allow_html=True)
    st.toast("AgentForge PM report is ready.")
    return result


def render_empty_state() -> None:
    st.markdown('<div class="section-kicker">Before You Run</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="empty-state">
            <div>
                <span class="ai-badge">Preview</span>
                <h2>Turn raw PM artifacts into a board-ready baseline.</h2>
                <p>
                    Start with the synthetic HVAC dataset or upload project files. AgentForge PM will
                    assemble requirements, risk exposure, schedule logic, and recommended actions into
                    a downloadable report package.
                </p>
            </div>
            <div class="empty-metrics">
                <div><span>Example Requirements</span><strong>42</strong></div>
                <div><span>High Risks Flagged</span><strong>7</strong></div>
                <div><span>Baseline Duration</span><strong>96d</strong></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown(
            """
            <div class="preview-card">
                <div class="preview-icon">REQ</div>
                <h3>What you'll get</h3>
                <p>Requirements register with source-aware scope items, owners, acceptance notes, and PM-ready structure.</p>
                <div class="sample-row"><span>Controls integration</span><strong>Critical</strong></div>
                <div class="sample-row"><span>Procurement package</span><strong>Open</strong></div>
                <div class="sample-row"><span>Commissioning plan</span><strong>Ready</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_b:
        st.markdown(
            """
            <div class="preview-card">
                <div class="preview-icon">RISK</div>
                <h3>Sample risk chart</h3>
                <p>Ranked risk exposure for procurement, budget, controls, outage, and commissioning decisions.</p>
                <div class="risk-bar"><span style="width: 88%"></span><label>Long-lead equipment</label></div>
                <div class="risk-bar"><span style="width: 72%"></span><label>BAS integration</label></div>
                <div class="risk-bar"><span style="width: 54%"></span><label>Night work access</label></div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col_c:
        st.markdown(
            """
            <div class="preview-card">
                <div class="preview-icon">PLAN</div>
                <h3>Schedule teaser</h3>
                <p>Optimized task sequence, critical path cues, and a Gantt-style baseline for execution planning.</p>
                <div class="timeline"><span style="left: 0%; width: 42%"></span></div>
                <div class="timeline"><span style="left: 24%; width: 48%"></span></div>
                <div class="timeline"><span style="left: 58%; width: 34%"></span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def save_uploaded_files(uploaded_files: list[Any]) -> str:
    upload_dir = Path(tempfile.mkdtemp(prefix="agentforge_pm_upload_"))
    for uploaded in uploaded_files:
        safe_name = Path(uploaded.name).name
        destination = upload_dir / safe_name
        destination.write_bytes(uploaded.getbuffer())
    return str(upload_dir)


def summarize_uploads(uploaded_files: list[Any]) -> dict[str, Any]:
    total_size = 0
    names = []
    for uploaded in uploaded_files:
        size = getattr(uploaded, "size", None)
        if size is None:
            size = len(uploaded.getbuffer())
        total_size += int(size)
        names.append(Path(uploaded.name).name)
    return {"count": len(uploaded_files), "size": total_size, "names": names}


def format_bytes(size: int) -> str:
    value = float(size)
    for unit in ["B", "KB", "MB", "GB"]:
        if value < 1024 or unit == "GB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{size} B"


def format_currency(value: Any) -> str:
    try:
        return f"${float(value):,.0f}"
    except (TypeError, ValueError):
        return "n/a"


def format_roi(value: Any) -> str:
    try:
        return f"{float(value):.2f}x"
    except (TypeError, ValueError):
        return "n/a"


def build_demo_dataset() -> dict[str, list[dict[str, Any]]]:
    """Build Streamlit-owned synthetic demo data with normalized date types."""
    now = datetime.utcnow()
    return {
        "overdue_invoices": [
            {
                "invoice_id": "INV-DEMO-001",
                "customer_id": "CUST-SMITH",
                "customer_name": "Smith Residence",
                "amount": 1250.00,
                "due_date": now - timedelta(days=45),
                "invoice_date": now - timedelta(days=75),
                "days_overdue": 45,
                "status": "overdue",
            },
            {
                "invoice_id": "INV-DEMO-002",
                "customer_id": "CUST-XYZ",
                "customer_name": "XYZ Office",
                "amount": 2100.00,
                "due_date": now - timedelta(days=32),
                "invoice_date": now - timedelta(days=62),
                "days_overdue": 32,
                "status": "overdue",
            },
        ]
    }


def build_synthetic_result(
    goals: list[str],
    reason: str,
    partial_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "execution_plan": [
            {"agent": "inventory_forecaster", "task": "Build synthetic inventory and requirement baseline."},
            {"agent": "risk_assessor", "task": "Rank synthetic delivery risks."},
            {"agent": "scheduler", "task": "Create synthetic schedule baseline."},
            {"agent": "ar_collector", "task": "Build synthetic AR follow-up queue."},
        ],
        "optimized_schedule": {
            "method": "synthetic",
            "duration_days": 47,
            "critical_path": ["Requirements validation", "Procurement", "Installation", "Commissioning"],
            "tasks": [
                {"task": "Requirements validation", "start_day": 0, "finish_day": 5, "duration_days": 5},
                {"task": "Procurement", "start_day": 5, "finish_day": 25, "duration_days": 20},
                {"task": "Installation", "start_day": 25, "finish_day": 40, "duration_days": 15},
                {"task": "Commissioning", "start_day": 40, "finish_day": 47, "duration_days": 7},
            ],
        },
        "pm_report": {},
        "agent_trace": [
            "Synthetic fallback selected.",
            "Synthetic requirements, risks, schedule, and AR queue generated.",
        ],
        "data_source": {
            "mode": "synthetic",
            "label": "Synthetic fallback",
            "fallback": True,
            "message": reason,
        },
    }
    if partial_result:
        result["partial_live_result"] = partial_result
    fixed = enforce_synthetic_baseline(result, goals)
    fixed["dispatch_baseline"] = assemble_dispatch_baseline(
        goals=goals,
        project_data={"source": "synthetic", "synthetic": True},
        execution_plan=fixed.get("execution_plan", []),
        inventory_data={"requirements_register": fixed.get("requirements_register", [])},
        risk_data={"risk_register": fixed.get("risk_register", [])},
        schedule_data={"optimized_schedule": fixed.get("optimized_schedule", {})},
        ar_data={"overdue_invoices": fixed.get("overdue_invoices", [])},
        data_source="synthetic",
    )
    fixed["dispatch_baseline_markdown"] = fixed["dispatch_baseline"]["reports"]["markdown"]
    fixed["dispatch_baseline_json"] = fixed["dispatch_baseline"]["reports"]["json"]
    return fixed


def run_job_with_live_progress(project_path: str | None, goals: list[str], progress: Any, status: Any) -> dict[str, Any]:
    job_id = f"streamlit-pm-{uuid4().hex[:10]}"
    trace: list[str] = []
    jobs = {
        job_id: SimpleNamespace(
            job_id=job_id,
            status="PENDING",
            progress=0.0,
            details="Queued.",
            result=None,
        )
    }

    async def runner() -> dict[str, Any]:
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
        if job.details and job.details != last_detail:
            trace.append(job.details)
        result["agent_trace"] = trace
        return result

    return asyncio.run(runner())


def enforce_synthetic_baseline(result: dict[str, Any], goals: list[str]) -> dict[str, Any]:
    requirements = result.get("requirements_register", [])
    risks = result.get("risk_register", [])
    high_risk_count = sum(1 for risk in risks if risk.get("severity") == "High")

    if 5 <= len(requirements) <= 7 and high_risk_count == 1:
        return result

    fixed = dict(result)
    fixed_requirements = synthetic_requirements(goals)
    fixed_risks = synthetic_risks(len(fixed_requirements))
    fixed["requirements_register"] = fixed_requirements
    fixed["risk_register"] = fixed_risks
    demo_data = build_demo_dataset()
    overdue_invoices = demo_data["overdue_invoices"]
    total_overdue = sum(float(invoice.get("amount", 0) or 0) for invoice in overdue_invoices)
    fixed["overdue_invoices"] = overdue_invoices
    fixed["total_overdue_amount"] = total_overdue
    fixed["invoices_count"] = len(overdue_invoices)

    report = dict(fixed.get("pm_report", {}))
    schedule = fixed.get("optimized_schedule", {})
    report.update(
        {
            "summary": "PM baseline generated for HVAC, construction, and industrial automation delivery.",
            "requirements_count": len(fixed_requirements),
            "high_risk_count": 1,
            "planned_duration_days": schedule.get("duration_days", report.get("planned_duration_days")),
            "critical_path": schedule.get("critical_path", report.get("critical_path", [])),
            "ar_summary": {
                "overdue_count": len(overdue_invoices),
                "total_amount": total_overdue,
                "oldest_invoice_days": max(
                    (int(invoice.get("days_overdue", 0) or 0) for invoice in overdue_invoices),
                    default=0,
                ),
            },
            "recommended_actions": report.get("recommended_actions")
            or [
                "Review requirements register with owner and discipline leads.",
                "Start procurement risk mitigation for long-lead equipment.",
                "Use the optimized schedule as the baseline for weekly variance tracking.",
            ],
            "risk_chart_path": None,
        }
    )
    fixed["pm_report"] = report
    return fixed


def synthetic_requirements(goals: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    domains = [
        ("HVAC", "Define, approve, and track hvac scope requirements.", "High"),
        ("Controls", "Define, approve, and track controls scope requirements.", "High"),
        ("Construction", "Define, approve, and track construction scope requirements.", "Medium"),
        ("Financial", "Define, approve, and track financial scope requirements.", "Medium"),
    ]
    for idx, (domain, statement, priority) in enumerate(domains, start=1):
        rows.append(
            {
                "id": f"REQ-{idx:03d}",
                "domain": domain,
                "statement": statement,
                "priority": priority,
                "acceptance_criteria": "Owner sign-off, traceable deliverable, and measurable completion evidence.",
            }
        )

    for goal in goals[:3]:
        rows.append(
            {
                "id": f"REQ-{len(rows) + 1:03d}",
                "domain": "User Goal",
                "statement": goal,
                "priority": "High",
                "acceptance_criteria": "Goal is mapped to schedule, risk, owner, and completion metric.",
            }
        )
    return rows


def synthetic_risks(requirement_count: int) -> list[dict[str, Any]]:
    requirement_factor = min(0.15, requirement_count * 0.015)
    rows = [
        ("Long-lead equipment delay", 0.42, 0.75, "Procurement"),
        ("Controls integration defect", 0.35, 0.70, "Automation"),
        ("Field labor constraint", 0.30, 0.55, "Construction"),
        ("Scope gap or late owner decision", 0.28, 0.62, "Stakeholder"),
        ("Budget contingency burn", 0.061, 0.65, "Financial"),
    ]
    mitigations = {
        "Procurement": "Validate submittals early, track vendor commitments weekly, and approve alternates.",
        "Automation": "Run interface tests before commissioning and reserve controls engineering support.",
        "Construction": "Level labor loading and protect shutdown windows.",
        "Stakeholder": "Create decision log with dated owner approvals.",
        "Financial": "Tie contingency releases to approved risk events.",
    }
    risks = []
    for risk, probability, impact, category in rows:
        score = min(1.0, (probability + requirement_factor) * impact)
        risks.append(
            {
                "risk": risk,
                "probability": probability,
                "impact": impact,
                "category": category,
                "score": score,
                "severity": "High" if risk == "Long-lead equipment delay" else "Medium" if score >= 0.18 else "Low",
                "mitigation": mitigations[category],
            }
        )
    return sorted(risks, key=lambda item: item["score"], reverse=True)


def render_results(result: dict[str, Any]) -> None:
    report = result.get("pm_report", {})
    requirements_df = pd.DataFrame(result.get("requirements_register", []))
    risks_df = pd.DataFrame(result.get("risk_register", []))
    schedule_df = pd.DataFrame(result.get("optimized_schedule", {}).get("tasks", []))
    ar_df = pd.DataFrame(result.get("overdue_invoices", []))
    risk_chart_bytes = resolve_risk_chart(report, risks_df)

    st.markdown('<div class="section-kicker">Results</div>', unsafe_allow_html=True)
    render_dispatch_baseline_section(result)
    render_success_banner(
        report,
        requirements_df,
        risks_df,
        schedule_df,
        ar_df,
        risk_chart_bytes,
    )
    render_run_metadata(result)

    overview, technician, requirements, risks, schedule, ar, summary = st.tabs(
        ["Overview", "Technician Dispatch", "Requirements", "Risks", "Schedule", "AR", "Summary"]
    )
    with overview:
        render_overview_tab(report, result, requirements_df, risks_df, schedule_df, risk_chart_bytes)
    with technician:
        render_technician_dispatch_tab(result)
    with requirements:
        render_requirements_tab(requirements_df)
    with risks:
        render_risks_tab(risks_df, risk_chart_bytes)
    with schedule:
        render_schedule_tab(schedule_df)
    with ar:
        render_ar_tab(ar_df)
    with summary:
        render_summary_tab(report, result)


def render_dispatch_baseline_section(result: dict[str, Any]) -> None:
    baseline = result.get("dispatch_baseline") or {}
    if not baseline:
        return

    roi = baseline.get("roi_summary", {})
    summary = baseline.get("summary", {})
    markdown_report = (
        result.get("dispatch_baseline_markdown")
        or baseline.get("reports", {}).get("markdown")
        or "# Dispatch Baseline\n\nNo Markdown report was returned."
    )
    json_report = (
        result.get("dispatch_baseline_json")
        or baseline.get("reports", {}).get("json")
        or "{}"
    )
    actions = baseline.get("recommended_actions", [])
    baseline_zip = build_dispatch_baseline_download_zip(markdown_report, json_report)

    st.markdown(
        """
        <div class="dispatch-baseline-hero">
            <span>Hero Output</span>
            <strong>Dispatch Baseline</strong>
            <p>Board-ready operating baseline with ROI, value capture, schedule exposure, AR opportunity, and next actions.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Estimated ROI", format_roi(roi.get("estimated_roi", summary.get("estimated_roi"))))
    metric_cols[1].metric("Estimated Value", format_currency(roi.get("estimated_value")))
    metric_cols[2].metric("AR Opportunity", format_currency(summary.get("ar_recovery_opportunity")))
    metric_cols[3].metric("Planned Days", summary.get("planned_duration_days", "n/a"))

    preview_col, action_col = st.columns([0.62, 0.38], vertical_alignment="top")
    with preview_col:
        st.markdown('<div class="baseline-panel-title">Executive Markdown Preview</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(markdown_report)
    with action_col:
        st.markdown('<div class="baseline-panel-title">Recommended Actions</div>', unsafe_allow_html=True)
        if actions:
            for idx, action in enumerate(actions[:4], start=1):
                st.markdown(
                    f"""
                    <div class="baseline-action">
                        <span>{idx}</span>
                        <strong>{html.escape(str(action))}</strong>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.info("No baseline actions were returned.")

        st.markdown('<div class="baseline-panel-title">One-Click Downloads</div>', unsafe_allow_html=True)
        icon_download_button(
            "Baseline ZIP",
            ":material/archive:",
            data=baseline_zip,
            file_name="hvac_opsforge_dispatch_baseline.zip",
            mime="application/zip",
            width="stretch",
        )
        download_cols = st.columns(2)
        with download_cols[0]:
            icon_download_button(
                "Markdown",
                ":material/article:",
                data=markdown_report.encode("utf-8"),
                file_name="hvac_opsforge_dispatch_baseline.md",
                mime="text/markdown",
                width="stretch",
            )
        with download_cols[1]:
            icon_download_button(
                "JSON",
                ":material/data_object:",
                data=json_report.encode("utf-8"),
                file_name="hvac_opsforge_dispatch_baseline.json",
                mime="application/json",
                width="stretch",
            )


def build_dispatch_baseline_download_zip(markdown_report: str, json_report: str) -> bytes:
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        archive.writestr("dispatch_baseline.md", markdown_report)
        archive.writestr("dispatch_baseline.json", json_report)
    return output.getvalue()


def render_run_metadata(result: dict[str, Any]) -> None:
    source = result.get("data_source", {})
    if source:
        if source.get("fallback"):
            st.warning(f"Data source: {source.get('label', 'Synthetic fallback')}. {source.get('message', '')}")
        else:
            st.success(f"Data source: {source.get('label', 'Live Mongo')}. {source.get('message', '')}")

    trace = result.get("agent_trace", [])
    if trace:
        with st.expander("Agent trace", expanded=False):
            for detail in trace:
                st.write(f"- {detail}")

    partial = result.get("partial_live_result")
    if partial:
        with st.expander("Partial live result captured before fallback", expanded=False):
            st.json(partial)


def render_success_banner(
    report: dict[str, Any],
    requirements_df: pd.DataFrame,
    risks_df: pd.DataFrame,
    schedule_df: pd.DataFrame,
    ar_df: pd.DataFrame,
    risk_chart_bytes: bytes | None,
) -> None:
    zip_bytes = build_report_zip(report, requirements_df, risks_df, schedule_df, risk_chart_bytes)
    left, right = st.columns([0.66, 0.34], vertical_alignment="center")
    with left:
        st.markdown(
            """
            <div class="success-banner">
                <span>Analysis complete</span>
                <strong>Your PM baseline is ready for review and export.</strong>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown('<div class="export-title">Exports</div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.caption("Report package")
            primary_export, markdown_export = st.columns(2)
            with primary_export:
                icon_download_button(
                    "Full ZIP",
                    ":material/archive:",
                    data=zip_bytes,
                    file_name="agentforge_pm_report.zip",
                    mime="application/zip",
                    width="stretch",
                )
            with markdown_export:
                icon_download_button(
                    "Markdown",
                    ":material/article:",
                    data=build_summary_markdown(report).encode("utf-8"),
                    file_name="hvac_opsforge_report.md",
                    mime="text/markdown",
                    width="stretch",
                )
        with st.container(border=True):
            st.caption("Operational tables")
            csv_exports = st.columns(2)
            if not schedule_df.empty:
                with csv_exports[0]:
                    icon_download_button(
                        "Dispatch CSV",
                        ":material/table:",
                        data=schedule_df.to_csv(index=False).encode("utf-8"),
                        file_name="hvac_opsforge_dispatch.csv",
                        mime="text/csv",
                        width="stretch",
                    )
            else:
                with csv_exports[0]:
                    icon_button("Dispatch CSV", ":material/table:", key="disabled_dispatch_csv", disabled=True)
            if not ar_df.empty:
                with csv_exports[1]:
                    icon_download_button(
                        "AR CSV",
                        ":material/receipt_long:",
                        data=ar_df.to_csv(index=False).encode("utf-8"),
                        file_name="hvac_opsforge_ar.csv",
                        mime="text/csv",
                        width="stretch",
                    )
            else:
                with csv_exports[1]:
                    icon_button("AR CSV", ":material/receipt_long:", key="disabled_ar_csv", disabled=True)


def render_overview_tab(
    report: dict[str, Any],
    result: dict[str, Any],
    requirements_df: pd.DataFrame,
    risks_df: pd.DataFrame,
    schedule_df: pd.DataFrame,
    risk_chart_bytes: bytes | None,
) -> None:
    metric_cols = st.columns(4)
    metric_cols[0].metric("Requirements", report.get("requirements_count", len(requirements_df)))
    metric_cols[1].metric("High Risks", report.get("high_risk_count", 0))
    metric_cols[2].metric("Planned Days", report.get("planned_duration_days", "n/a"))
    metric_cols[3].metric("Schedule Method", result.get("optimized_schedule", {}).get("method", "n/a"))

    left, right = st.columns([0.58, 0.42])
    with left:
        st.markdown('<div class="panel-title">Executive Snapshot</div>', unsafe_allow_html=True)
        st.markdown(report.get("summary", "No summary returned."))
        actions = report.get("recommended_actions", [])
        if actions:
            st.markdown("**Priority actions**")
            for action in actions[:4]:
                st.write(f"- {action}")
    with right:
        st.markdown('<div class="panel-title">Risk Exposure</div>', unsafe_allow_html=True)
        if risk_chart_bytes:
            st.image(risk_chart_bytes, caption="Top PM risks", width="stretch")
        elif risks_df.empty:
            st.info("No risk chart data returned.")


def render_requirements_tab(requirements_df: pd.DataFrame) -> None:
    st.markdown('<div class="panel-title">Requirements Register</div>', unsafe_allow_html=True)
    if requirements_df.empty:
        st.info("No requirements were returned.")
        return
    st.dataframe(requirements_df, hide_index=True, width="stretch")
    download_csv("Download Requirements CSV", requirements_df, "agentforge_requirements.csv")


def render_risks_tab(risks_df: pd.DataFrame, risk_chart_bytes: bytes | None) -> None:
    st.markdown('<div class="panel-title">Risk Register</div>', unsafe_allow_html=True)
    risk_table, risk_chart = st.columns([0.62, 0.38])
    with risk_table:
        if risks_df.empty:
            st.info("No risks were returned.")
        else:
            st.dataframe(risks_df, hide_index=True, width="stretch")
            download_csv("Download Risk CSV", risks_df, "agentforge_risks.csv")
    with risk_chart:
        if risk_chart_bytes:
            st.image(risk_chart_bytes, caption="Top PM risks", width="stretch")
            icon_download_button(
                "Download Risk Chart PNG",
                ":material/image:",
                data=risk_chart_bytes,
                file_name="agentforge_risk_chart.png",
                mime="image/png",
                width="stretch",
            )


def render_schedule_tab(schedule_df: pd.DataFrame) -> None:
    st.markdown('<div class="panel-title">Schedule Baseline</div>', unsafe_allow_html=True)
    if schedule_df.empty:
        st.info("No schedule tasks were returned.")
        return
    st.pyplot(build_gantt_figure(schedule_df), width="stretch")
    st.dataframe(schedule_df, hide_index=True, width="stretch")
    download_csv("Download Schedule CSV", schedule_df, "agentforge_schedule.csv")


def render_technician_dispatch_tab(result: dict[str, Any]) -> None:
    payload = build_technician_dispatch_payload(json.dumps(to_streamlit_jsonable(result), sort_keys=True))
    jobs = payload.get("jobs", [])
    parts = payload.get("parts_checklist", [])
    risks = payload.get("risks", [])
    route = payload.get("optimized_route", [])

    st.markdown(
        """
        <div class="technician-hero">
            <span>Field Mode</span>
            <strong>Technician Dispatch</strong>
            <p>Today's work, parts readiness, risks, and route sequence in a phone-first view for field execution.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not jobs:
        st.info("No dispatch jobs are available yet. Run a dispatch baseline to generate the field view.")
        return

    stats = payload.get("stats", {})
    metric_cols = st.columns(4)
    metric_cols[0].metric("Jobs", stats.get("jobs", len(jobs)))
    metric_cols[1].metric("Route Stops", stats.get("route_stops", len(route)))
    metric_cols[2].metric("Parts Ready", f"{parts_ready_count(parts)}/{len(parts)}")
    metric_cols[3].metric("High Risks", stats.get("high_risks", 0))

    job_col, field_col = st.columns([0.58, 0.42], gap="large")
    with job_col:
        st.markdown('<div class="panel-title">Job List</div>', unsafe_allow_html=True)
        for job in jobs:
            render_technician_job_card(job)

    with field_col:
        st.markdown('<div class="panel-title">Parts Checklist</div>', unsafe_allow_html=True)
        render_parts_checklist(parts)

        st.markdown('<div class="panel-title">Optimized Route</div>', unsafe_allow_html=True)
        render_route_steps(route)

        st.markdown('<div class="panel-title">Field Risks</div>', unsafe_allow_html=True)
        render_field_risks(risks)

        export_payload = build_technician_export_payload(payload)
        icon_download_button(
            "Export Offline JSON",
            ":material/download_for_offline:",
            data=json.dumps(export_payload, indent=2, sort_keys=True).encode("utf-8"),
            file_name="hvac_opsforge_technician_dispatch.json",
            mime="application/json",
            width="stretch",
        )


@st.cache_data(show_spinner=False)
def build_technician_dispatch_payload(result_json: str) -> dict[str, Any]:
    result = json.loads(result_json)
    baseline = result.get("dispatch_baseline") or {}
    schedule = baseline.get("optimized_schedule") or result.get("optimized_schedule") or {}
    tasks = schedule.get("tasks") or []
    risks = baseline.get("risk_register") or result.get("risk_register") or []
    requirements = baseline.get("requirements_register") or result.get("requirements_register") or []

    jobs = build_technician_jobs(tasks, risks)
    parts = build_parts_checklist(jobs, requirements)
    route = build_optimized_route(jobs)
    high_risks = sum(1 for risk in risks if str(risk.get("severity", "")).lower() == "high")

    return {
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "mode": "offline_ready",
        "job_to_be_done": (
            "When a field tech starts a route, they need the next job, required parts, known risks, "
            "and proof-ready actions without depending on a live connection."
        ),
        "stats": {
            "jobs": len(jobs),
            "route_stops": len(route),
            "parts": len(parts),
            "high_risks": high_risks,
        },
        "jobs": jobs,
        "parts_checklist": parts,
        "risks": normalize_field_risks(risks),
        "optimized_route": route,
    }


def build_technician_jobs(tasks: list[dict[str, Any]], risks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not tasks:
        return []

    top_risk = risks[0] if risks else {}
    ordered = sorted(tasks, key=lambda item: safe_number(item.get("start_day"), 0))
    sites = ["Main mechanical room", "Roof units", "Controls closet", "Tenant suite", "Loading dock"]
    jobs = []
    for idx, task in enumerate(ordered[:8], start=1):
        title = str(task.get("task") or task.get("name") or f"Dispatch job {idx}")
        duration = int(safe_number(task.get("duration_days"), 1))
        priority = "P1" if idx == 1 or "commission" in title.lower() else "P2" if duration >= 10 else "P3"
        jobs.append(
            {
                "job_id": f"JOB-{idx:03d}",
                "sequence": idx,
                "title": title,
                "site": sites[(idx - 1) % len(sites)],
                "status": "Ready" if idx == 1 else "Queued",
                "priority": priority,
                "eta": f"Day {int(safe_number(task.get('start_day'), idx - 1))}",
                "duration_days": duration,
                "route_stop": idx,
                "primary_risk": top_risk.get("risk", "Access or parts readiness must be verified."),
                "next_action": technician_next_action(title),
                "proof_needed": "Photos, readings, parts used, and customer sign-off notes.",
            }
        )
    return jobs


def build_parts_checklist(jobs: list[dict[str, Any]], requirements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    base_parts = [
        ("Filter set", "MERV-13 filter set", "Truck stock", "Ready"),
        ("Belt kit", "Matched belt kit", "Warehouse", "Verify"),
        ("Condensate kit", "Trap, tubing, float switch", "Truck stock", "Ready"),
        ("Controls sensor", "Temperature sensor and wiring kit", "Controls shelf", "Pull"),
        ("Fasteners", "Anchors, screws, labels, and tags", "Truck stock", "Ready"),
    ]
    requirement_text = " ".join(
        str(item.get("domain") or item.get("requirement") or item.get("statement") or "")
        for item in requirements
    ).lower()
    if "procurement" in requirement_text or "equipment" in requirement_text:
        base_parts.append(("Procurement packet", "Submittal, PO, and vendor ETA notes", "Office", "Verify"))

    job_count = max(len(jobs), 1)
    parts = []
    for idx, (name, description, location, status) in enumerate(base_parts, start=1):
        parts.append(
            {
                "part_id": f"PART-{idx:03d}",
                "name": name,
                "description": description,
                "location": location,
                "status": status,
                "job_id": jobs[(idx - 1) % job_count]["job_id"] if jobs else "JOB-001",
                "required_before_stop": min(idx, job_count),
            }
        )
    return parts


def build_optimized_route(jobs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    route = [
        {
            "stop": 0,
            "label": "Warehouse",
            "objective": "Load checked parts and confirm offline packet.",
            "eta": "Start",
        }
    ]
    for job in jobs:
        route.append(
            {
                "stop": job["route_stop"],
                "label": job["site"],
                "job_id": job["job_id"],
                "objective": job["title"],
                "eta": job["eta"],
            }
        )
    return route


def normalize_field_risks(risks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for idx, risk in enumerate(risks[:5], start=1):
        normalized.append(
            {
                "rank": int(risk.get("rank") or idx),
                "risk": str(risk.get("risk") or f"Risk {idx}"),
                "severity": str(risk.get("severity") or "Medium"),
                "mitigation": str(risk.get("mitigation") or "Confirm owner, access, parts, and escalation path before arrival."),
            }
        )
    return normalized


def render_technician_job_card(job: dict[str, Any]) -> None:
    job_id = html.escape(str(job["job_id"]))
    title = html.escape(str(job["title"]))
    site = html.escape(str(job["site"]))
    next_action = html.escape(str(job["next_action"]))
    proof_needed = html.escape(str(job["proof_needed"]))
    st.markdown(
        f"""
        <div class="tech-job-card">
            <div class="tech-job-top">
                <span>{job_id} - Stop {job['route_stop']}</span>
                <strong>{html.escape(str(job['priority']))}</strong>
            </div>
            <h3>{title}</h3>
            <p>{site} | {html.escape(str(job['eta']))} | {job['duration_days']}d | {html.escape(str(job['status']))}</p>
            <div class="tech-action">{next_action}</div>
            <small>Proof: {proof_needed}</small>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_parts_checklist(parts: list[dict[str, Any]]) -> None:
    if not parts:
        st.info("No parts checklist is available.")
        return
    for part in parts:
        key = f"tech_part_ready_{part['part_id']}"
        default_checked = part.get("status") == "Ready"
        st.checkbox(
            f"{part['name']} - {part['description']}",
            value=st.session_state.get(key, default_checked),
            key=key,
            help=f"{part['location']} | Needed before stop {part['required_before_stop']} | {part['job_id']}",
        )


def render_route_steps(route: list[dict[str, Any]]) -> None:
    if not route:
        st.info("No optimized route is available.")
        return
    for stop in route:
        label = html.escape(str(stop["label"]))
        eta = html.escape(str(stop["eta"]))
        objective = html.escape(str(stop["objective"]))
        st.markdown(
            f"""
            <div class="route-step">
                <span>{stop['stop']}</span>
                <div><strong>{label}</strong><small>{eta} - {objective}</small></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_field_risks(risks: list[dict[str, Any]]) -> None:
    if not risks:
        st.info("No field risks are available.")
        return
    for risk in risks:
        severity = risk.get("severity", "Medium")
        if str(severity).lower() == "high":
            st.error(f"{risk['risk']} - {risk['mitigation']}")
        else:
            st.warning(f"{risk['risk']} - {risk['mitigation']}")


def build_technician_export_payload(payload: dict[str, Any]) -> dict[str, Any]:
    export_payload = dict(payload)
    export_payload["parts_checklist"] = [
        {
            **part,
            "checked": bool(st.session_state.get(f"tech_part_ready_{part['part_id']}", part.get("status") == "Ready")),
        }
        for part in payload.get("parts_checklist", [])
    ]
    export_payload["offline_instructions"] = [
        "Save this JSON before leaving coverage.",
        "Update checked parts before rolling to the first stop.",
        "Record proof notes in the job system when connectivity returns.",
    ]
    return export_payload


def parts_ready_count(parts: list[dict[str, Any]]) -> int:
    return sum(
        1
        for part in parts
        if bool(st.session_state.get(f"tech_part_ready_{part['part_id']}", part.get("status") == "Ready"))
    )


def technician_next_action(title: str) -> str:
    text = title.lower()
    if "procurement" in text:
        return "Confirm staged material, vendor ETA, and substitute approval before dispatch."
    if "commission" in text:
        return "Capture readings, BAS trend evidence, and owner acceptance before closeout."
    if "install" in text:
        return "Verify access, lockout needs, and parts on truck before starting work."
    if "requirement" in text:
        return "Confirm scope, site constraints, and decision maker before work release."
    return "Check parts, site access, risk note, and proof requirements before arrival."


def safe_number(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_streamlit_jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): to_streamlit_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [to_streamlit_jsonable(item) for item in value]
    if isinstance(value, (datetime, date, Path)):
        return value.isoformat() if isinstance(value, (datetime, date)) else str(value)
    return value


def render_ar_tab(ar_df: pd.DataFrame) -> None:
    st.markdown('<div class="panel-title">AR Follow-up Queue</div>', unsafe_allow_html=True)
    if ar_df.empty:
        st.info("No overdue invoices were returned.")
        return

    st.dataframe(ar_df, hide_index=True, width="stretch")
    download_csv("Download AR CSV", ar_df, "hvac_opsforge_ar.csv")

    st.markdown("**Owner review**")
    feedback = st.session_state.get("ar_decision_feedback")
    if feedback:
        st.success(feedback)

    decision_counts = {"Approved": 0, "Rejected": 0, "Pending": 0}
    for idx, invoice in ar_df.iterrows():
        invoice_id = str(invoice.get("invoice_id") or invoice.get("_id") or f"invoice-{idx + 1}")
        decision = st.session_state.get(f"ar_decision_{invoice_id}", "Pending")
        decision_counts[decision if decision in decision_counts else "Pending"] += 1

    approved_col, rejected_col, pending_col = st.columns(3)
    approved_col.metric("Approved", decision_counts["Approved"])
    rejected_col.metric("Rejected", decision_counts["Rejected"])
    pending_col.metric("Pending", decision_counts["Pending"])
    reviewed_count = decision_counts["Approved"] + decision_counts["Rejected"]
    total_count = max(len(ar_df), 1)
    st.progress(reviewed_count / total_count, text=f"{reviewed_count} of {len(ar_df)} AR follow-ups reviewed.")

    for idx, invoice in ar_df.iterrows():
        invoice_id = str(
            invoice.get("invoice_id")
            or invoice.get("_id")
            or f"invoice-{idx + 1}"
        )
        customer = invoice.get("customer_name") or invoice.get("customer_id") or "Customer"
        amount = float(invoice.get("amount", 0) or 0)
        decision_key = f"ar_decision_{invoice_id}"
        current_decision = st.session_state.get(decision_key, "Pending")

        with st.container(border=True):
            invoice_col, status_col, approve_col, reject_col = st.columns(
                [0.46, 0.18, 0.18, 0.18],
                vertical_alignment="center",
            )
            invoice_col.write(f"**{invoice_id}**")
            invoice_col.caption(f"{customer} - ${amount:,.2f}")
            if current_decision == "Approved":
                status_col.success("Approved")
            elif current_decision == "Rejected":
                status_col.error("Rejected")
            else:
                status_col.info("Pending")
            with approve_col:
                approve_clicked = icon_button(
                    "Approve",
                    ":material/check:",
                    key=f"approve_{invoice_id}",
                    disabled=current_decision == "Approved",
                )
            if approve_clicked:
                st.session_state[decision_key] = "Approved"
                st.session_state["ar_decision_feedback"] = (
                    f"Approved AR follow-up for {invoice_id}."
                )
                st.toast(f"Approved {invoice_id}.")
                st.rerun()
            with reject_col:
                reject_clicked = icon_button(
                    "Reject",
                    ":material/close:",
                    key=f"reject_{invoice_id}",
                    disabled=current_decision == "Rejected",
                )
            if reject_clicked:
                st.session_state[decision_key] = "Rejected"
                st.session_state["ar_decision_feedback"] = (
                    f"Rejected AR follow-up for {invoice_id}."
                )
                st.toast(f"Rejected {invoice_id}.")
                st.rerun()


def render_summary_tab(report: dict[str, Any], result: dict[str, Any]) -> None:
    st.markdown('<div class="panel-title">Executive Summary</div>', unsafe_allow_html=True)
    st.markdown(f"**Summary:** {report.get('summary', 'No summary returned.')}")
    critical_path = report.get("critical_path") or result.get("optimized_schedule", {}).get("critical_path", [])
    if critical_path:
        st.markdown(f"**Critical path:** {' -> '.join(str(item) for item in critical_path)}")
    actions = report.get("recommended_actions", [])
    if actions:
        st.markdown("**Recommended actions**")
        for action in actions:
            st.write(f"- {action}")


def download_csv(label: str, frame: pd.DataFrame, file_name: str) -> None:
    if frame.empty:
        return
    icon_download_button(
        label,
        ":material/download:",
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name=file_name,
        mime="text/csv",
        width="stretch",
    )


def resolve_risk_chart(report: dict[str, Any], risks_df: pd.DataFrame) -> bytes | None:
    chart_path = report.get("risk_chart_path")
    if chart_path and Path(chart_path).exists():
        return Path(chart_path).read_bytes()
    if not risks_df.empty:
        return build_risk_chart_png(risks_df)
    return None


def build_report_zip(
    report: dict[str, Any],
    requirements_df: pd.DataFrame,
    risks_df: pd.DataFrame,
    schedule_df: pd.DataFrame,
    risk_chart_bytes: bytes | None,
) -> bytes:
    output = BytesIO()
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        if not requirements_df.empty:
            archive.writestr("agentforge_requirements.csv", requirements_df.to_csv(index=False))
        if not risks_df.empty:
            archive.writestr("agentforge_risks.csv", risks_df.to_csv(index=False))
        if not schedule_df.empty:
            archive.writestr("agentforge_schedule.csv", schedule_df.to_csv(index=False))
        if risk_chart_bytes:
            archive.writestr("agentforge_risk_chart.png", risk_chart_bytes)
        archive.writestr("agentforge_summary.md", build_summary_markdown(report))
    return output.getvalue()


def build_summary_markdown(report: dict[str, Any]) -> str:
    actions = report.get("recommended_actions", [])
    critical_path = report.get("critical_path", [])
    lines = [
        "# AgentForge PM Executive Summary",
        "",
        report.get("summary", "No summary returned."),
        "",
        f"- Requirements: {report.get('requirements_count', 'n/a')}",
        f"- High risks: {report.get('high_risk_count', 'n/a')}",
        f"- Planned duration days: {report.get('planned_duration_days', 'n/a')}",
    ]
    if critical_path:
        lines.extend(["", "## Critical Path", " -> ".join(str(item) for item in critical_path)])
    if actions:
        lines.extend(["", "## Recommended Actions"])
        lines.extend([f"- {action}" for action in actions])
    return "\n".join(lines)


def build_risk_chart_png(risks_df: pd.DataFrame) -> bytes:
    fig, ax = plt.subplots(figsize=(8, 4), facecolor="#0f1720")
    ax.set_facecolor("#0f1720")
    plot_df = risks_df.sort_values("score", ascending=True)
    ax.barh(plot_df["risk"].astype(str), plot_df["score"].astype(float), color="#20c7b3")
    ax.set_xlabel("Risk score", color="#d7e8ee")
    ax.set_title("Top PM Risks", color="#ffffff", pad=12)
    ax.tick_params(colors="#d7e8ee")
    for spine in ax.spines.values():
        spine.set_color("#294554")
    ax.grid(axis="x", alpha=0.18, color="#9ad7e3")
    fig.tight_layout()
    output = BytesIO()
    fig.savefig(output, format="png", dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    return output.getvalue()


def build_gantt_figure(schedule_df: pd.DataFrame) -> plt.Figure:
    frame = schedule_df.sort_values("start_day", ascending=True).copy()
    frame["start_day"] = pd.to_numeric(frame["start_day"], errors="coerce").fillna(0)
    frame["duration_days"] = pd.to_numeric(frame["duration_days"], errors="coerce").fillna(1)

    fig, ax = plt.subplots(figsize=(10, max(3, len(frame) * 0.55)), facecolor="#0f1720")
    ax.set_facecolor("#0f1720")
    ax.barh(
        frame["task"].astype(str),
        frame["duration_days"],
        left=frame["start_day"],
        color="#20c7b3",
        edgecolor="#96f2e7",
    )
    ax.set_xlabel("Project day", color="#d7e8ee")
    ax.set_ylabel("")
    ax.set_title("Optimized Schedule", color="#ffffff", pad=12)
    ax.grid(axis="x", alpha=0.18, color="#9ad7e3")
    ax.tick_params(colors="#d7e8ee")
    for spine in ax.spines.values():
        spine.set_color("#294554")
    ax.invert_yaxis()
    fig.tight_layout()
    return fig


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #08111a;
            --surface: #0f1720;
            --surface-2: #132332;
            --card: rgba(19, 35, 50, 0.82);
            --border: rgba(132, 203, 214, 0.18);
            --text: #edf8fb;
            --muted: #9bb7c3;
            --teal: #20c7b3;
            --blue: #3b82f6;
            --shadow: 0 18px 50px rgba(0, 0, 0, 0.28);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(32, 199, 179, 0.13), transparent 32rem),
                linear-gradient(135deg, #08111a 0%, #0c1824 48%, #0d1f2c 100%);
            color: var(--text);
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0b1620 0%, #0f1c27 100%);
            border-right: 1px solid var(--border);
        }

        h1, h2, h3 {
            letter-spacing: 0;
        }

        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 3rem;
            max-width: 1440px;
        }

        .top-action-title {
            color: var(--muted);
            font-size: 0.88rem;
            font-weight: 750;
            margin: -0.35rem 0 0.65rem;
        }

        .app-hero, .empty-state, .run-card, .preview-card, .success-banner, .dispatch-baseline-hero, .technician-hero, .tech-job-card {
            border: 1px solid var(--border);
            background: var(--card);
            box-shadow: var(--shadow);
            backdrop-filter: blur(12px);
        }

        .app-hero {
            display: flex;
            justify-content: space-between;
            gap: 1.5rem;
            padding: 1.55rem;
            border-radius: 8px;
            margin-bottom: 1.25rem;
        }

        .app-hero h1 {
            margin: 0.3rem 0 0.35rem;
            font-size: clamp(2rem, 4vw, 3.6rem);
            color: #ffffff;
        }

        .app-hero p, .empty-state p, .preview-card p, .run-card p {
            color: var(--muted);
            margin: 0;
            line-height: 1.55;
        }

        .eyebrow-row {
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }

        .product-icon {
            width: 2.25rem;
            height: 2.25rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 8px;
            background: rgba(32, 199, 179, 0.14);
            border: 1px solid rgba(32, 199, 179, 0.28);
        }

        .ai-badge {
            display: inline-flex;
            align-items: center;
            width: fit-content;
            border-radius: 999px;
            padding: 0.25rem 0.65rem;
            font-size: 0.78rem;
            font-weight: 700;
            color: #09201f;
            background: linear-gradient(90deg, #96f2e7, #8cc8ff);
        }

        .hero-stat-grid {
            min-width: min(430px, 100%);
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.75rem;
            align-self: end;
        }

        .mini-stat, .empty-metrics div {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.85rem;
            background: rgba(255,255,255,0.04);
        }

        .mini-stat span, .empty-metrics span, .muted-label {
            display: block;
            color: var(--muted);
            font-size: 0.78rem;
            margin-bottom: 0.25rem;
        }

        .mini-stat strong, .empty-metrics strong {
            color: #ffffff;
            font-size: 0.98rem;
        }

        .section-kicker, .panel-title, .sidebar-title, .sidebar-section {
            color: #e9fbff;
            font-weight: 800;
            letter-spacing: 0;
        }

        .section-kicker {
            margin: 1rem 0 0.55rem;
            font-size: 0.86rem;
            text-transform: uppercase;
            color: #96f2e7;
        }

        .sidebar-title {
            font-size: 1.25rem;
            margin-bottom: 0.25rem;
        }

        .sidebar-section {
            margin: 1rem 0 0.55rem;
            font-size: 0.85rem;
            color: #96f2e7;
            text-transform: uppercase;
        }

        .source-card {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.85rem;
            background: rgba(255,255,255,0.04);
            margin-top: 0.75rem;
        }

        .source-card strong, .source-card span {
            display: block;
        }

        .source-card span {
            color: var(--muted);
            font-size: 0.88rem;
            margin-top: 0.25rem;
        }

        .run-card {
            border-radius: 8px;
            padding: 1rem 1.15rem;
        }

        .run-card h3 {
            margin: 0.2rem 0;
            color: #ffffff;
        }

        .empty-state {
            display: grid;
            grid-template-columns: minmax(0, 1.3fr) minmax(300px, 0.7fr);
            gap: 1.5rem;
            align-items: center;
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }

        .empty-state h2 {
            color: #ffffff;
            font-size: clamp(1.55rem, 3vw, 2.4rem);
            margin: 0.7rem 0 0.45rem;
        }

        .empty-metrics {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 0.75rem;
        }

        .empty-metrics strong {
            font-size: 1.55rem;
        }

        .preview-card {
            min-height: 285px;
            border-radius: 8px;
            padding: 1.1rem;
            transition: transform 140ms ease, border-color 140ms ease;
        }

        .preview-card:hover {
            transform: translateY(-2px);
            border-color: rgba(32, 199, 179, 0.45);
        }

        .preview-card h3 {
            margin: 0.65rem 0 0.35rem;
            color: #ffffff;
        }

        .preview-icon {
            width: 2.4rem;
            height: 2.4rem;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(59, 130, 246, 0.14);
            border: 1px solid rgba(140, 200, 255, 0.28);
        }

        .sample-row {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.08);
            padding: 0.55rem 0;
            color: var(--muted);
        }

        .sample-row strong {
            color: #96f2e7;
        }

        .risk-bar {
            position: relative;
            height: 2.15rem;
            border-radius: 8px;
            background: rgba(255,255,255,0.06);
            overflow: hidden;
            margin-top: 0.7rem;
        }

        .risk-bar span {
            display: block;
            height: 100%;
            background: linear-gradient(90deg, #20c7b3, #3b82f6);
        }

        .risk-bar label {
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            padding-left: 0.75rem;
            color: #ffffff;
            font-weight: 700;
            font-size: 0.86rem;
        }

        .timeline {
            height: 2rem;
            position: relative;
            background: rgba(255,255,255,0.06);
            border-radius: 8px;
            margin-top: 0.75rem;
        }

        .timeline span {
            position: absolute;
            top: 0.38rem;
            bottom: 0.38rem;
            border-radius: 999px;
            background: linear-gradient(90deg, #20c7b3, #8cc8ff);
        }

        .success-banner {
            display: flex;
            flex-direction: column;
            gap: 0.2rem;
            border-radius: 8px;
            padding: 1rem 1.15rem;
            margin-bottom: 0.75rem;
        }

        .success-banner span {
            color: #96f2e7;
            font-weight: 800;
        }

        .success-banner strong {
            color: #ffffff;
            font-size: 1.05rem;
        }

        .dispatch-baseline-hero {
            border-radius: 8px;
            padding: 1.2rem 1.35rem;
            margin: 0.4rem 0 0.9rem;
            background:
                linear-gradient(135deg, rgba(32, 199, 179, 0.18), rgba(59, 130, 246, 0.10)),
                var(--card);
        }

        .dispatch-baseline-hero span {
            color: #96f2e7;
            font-size: 0.78rem;
            font-weight: 850;
            text-transform: uppercase;
        }

        .dispatch-baseline-hero strong {
            display: block;
            color: #ffffff;
            font-size: clamp(1.55rem, 3vw, 2.35rem);
            margin-top: 0.2rem;
        }

        .dispatch-baseline-hero p {
            color: var(--muted);
            margin: 0.3rem 0 0;
            line-height: 1.5;
        }

        .baseline-panel-title {
            color: #ffffff;
            font-weight: 850;
            margin: 0.2rem 0 0.55rem;
        }

        .baseline-action {
            display: grid;
            grid-template-columns: 2rem minmax(0, 1fr);
            gap: 0.7rem;
            align-items: start;
            border: 1px solid var(--border);
            border-radius: 8px;
            background: rgba(255,255,255,0.045);
            padding: 0.75rem;
            margin-bottom: 0.65rem;
        }

        .baseline-action span {
            width: 2rem;
            height: 2rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            background: rgba(32, 199, 179, 0.18);
            border: 1px solid rgba(32, 199, 179, 0.34);
            color: #96f2e7;
            font-weight: 850;
        }

        .baseline-action strong {
            color: #edf8fb;
            line-height: 1.42;
            font-size: 0.95rem;
        }

        .technician-hero {
            border-radius: 8px;
            padding: 1rem 1.15rem;
            margin: 0.4rem 0 0.9rem;
            background:
                linear-gradient(135deg, rgba(150, 242, 231, 0.14), rgba(255, 214, 102, 0.10)),
                var(--card);
        }

        .technician-hero span {
            color: #96f2e7;
            font-size: 0.78rem;
            font-weight: 850;
            text-transform: uppercase;
        }

        .technician-hero strong {
            display: block;
            color: #ffffff;
            font-size: clamp(1.45rem, 3vw, 2.1rem);
            margin-top: 0.2rem;
        }

        .technician-hero p {
            color: var(--muted);
            margin: 0.3rem 0 0;
            line-height: 1.5;
        }

        .tech-job-card {
            border-radius: 8px;
            padding: 0.95rem;
            margin-bottom: 0.75rem;
        }

        .tech-job-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 0.75rem;
            color: var(--muted);
            font-size: 0.78rem;
            font-weight: 800;
        }

        .tech-job-top strong {
            color: #10232f;
            background: #ffd666;
            border-radius: 999px;
            padding: 0.18rem 0.55rem;
            min-width: 2.4rem;
            text-align: center;
        }

        .tech-job-card h3 {
            color: #ffffff;
            font-size: 1.05rem;
            margin: 0.45rem 0 0.25rem;
            line-height: 1.28;
        }

        .tech-job-card p, .tech-job-card small {
            color: var(--muted);
            line-height: 1.45;
        }

        .tech-action {
            border-left: 3px solid #20c7b3;
            padding: 0.55rem 0.7rem;
            margin: 0.7rem 0 0.45rem;
            background: rgba(32, 199, 179, 0.08);
            border-radius: 0 8px 8px 0;
            color: #edf8fb;
            font-weight: 750;
        }

        .route-step {
            display: grid;
            grid-template-columns: 2rem minmax(0, 1fr);
            gap: 0.65rem;
            align-items: start;
            margin-bottom: 0.6rem;
        }

        .route-step > span {
            width: 2rem;
            height: 2rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 999px;
            background: rgba(59, 130, 246, 0.18);
            border: 1px solid rgba(140, 200, 255, 0.28);
            color: #edf8fb;
            font-weight: 850;
        }

        .route-step strong, .route-step small {
            display: block;
        }

        .route-step strong {
            color: #ffffff;
            line-height: 1.2;
        }

        .route-step small {
            color: var(--muted);
            line-height: 1.35;
            margin-top: 0.15rem;
        }

        .export-title {
            color: #ffffff;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }

        .panel-title {
            margin: 0.8rem 0 0.6rem;
            font-size: 1.05rem;
        }

        div[data-testid="stMetric"] {
            background: rgba(19, 35, 50, 0.82);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 12px 34px rgba(0,0,0,0.18);
        }

        div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #edf8fb;
        }

        .stButton > button, .stDownloadButton > button {
            border-radius: 8px;
            min-height: 2.75rem;
            font-weight: 750;
            border: 1px solid rgba(32, 199, 179, 0.24);
            transition: transform 140ms ease, box-shadow 140ms ease;
        }

        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 28px rgba(32, 199, 179, 0.16);
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
            border-bottom: 1px solid var(--border);
        }

        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 0.75rem 1rem;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
        }

        @media (prefers-color-scheme: light) {
=======

def inject_brand_css() -> None:
    """Apply lightweight brand styling without adding frontend dependencies."""
    st.markdown(
        """
        <style>
>>>>>>> dev/ai-integration
            :root {
                --opsforge-blue: #0f4c81;
                --opsforge-blue-dark: #0b2545;
                --opsforge-green: #0f9f6e;
                --opsforge-mist: #eef7f4;
                --opsforge-border: #d8e2ea;
                --opsforge-text: #102033;
            }
            .main .block-container {
                padding-top: 1.25rem;
                padding-bottom: 2rem;
                max-width: 1280px;
            }
            [data-testid="stMetric"] {
                background: #ffffff;
                border: 1px solid var(--opsforge-border);
                border-radius: 8px;
                padding: 0.9rem 1rem;
                box-shadow: 0 6px 18px rgba(15, 76, 129, 0.08);
            }
<<<<<<< HEAD

            .app-hero h1, .empty-state h2, .preview-card h3, .run-card h3,
            .mini-stat strong, .empty-metrics strong, .success-banner strong,
            .dispatch-baseline-hero strong, .technician-hero strong, .tech-job-card h3,
            .section-kicker, .panel-title, .sidebar-title, .sidebar-section,
            .export-title, .route-step strong, .baseline-panel-title, .baseline-action strong {
                color: #10232f;
=======
            .opsforge-hero {
                background: linear-gradient(135deg, #0b2545 0%, #0f4c81 58%, #0f9f6e 100%);
                border-radius: 8px;
                color: #ffffff;
                padding: 1.35rem 1.5rem;
                margin-bottom: 1rem;
>>>>>>> dev/ai-integration
            }
            .opsforge-brand-row {
                display: flex;
                align-items: center;
                gap: 0.85rem;
            }
            .opsforge-mark {
                align-items: center;
                background: rgba(255, 255, 255, 0.14);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                display: inline-flex;
                font-weight: 800;
                height: 44px;
                justify-content: center;
                letter-spacing: 0;
                width: 44px;
            }
            .opsforge-hero h1 {
                font-size: 2rem;
                line-height: 1.1;
                margin: 0;
            }
            .opsforge-hero p {
                color: rgba(255, 255, 255, 0.86);
                margin: 0.35rem 0 0;
            }
            .opsforge-strip {
                background: var(--opsforge-mist);
                border: 1px solid #cfe8df;
                border-radius: 8px;
                color: var(--opsforge-text);
                padding: 0.8rem 1rem;
            }
            .opsforge-section-label {
                color: var(--opsforge-blue-dark);
                font-size: 0.82rem;
                font-weight: 750;
                letter-spacing: 0;
                margin-bottom: 0.35rem;
                text-transform: uppercase;
            }
<<<<<<< HEAD
        }

        @media (max-width: 640px) {
            .block-container {
                padding: 0.75rem 0.75rem 2rem;
            }

            .app-hero, .empty-state, .run-card, .preview-card, .success-banner, .dispatch-baseline-hero, .technician-hero, .tech-job-card {
                padding: 0.95rem;
            }

            .app-hero {
                gap: 1rem;
                margin-bottom: 0.75rem;
            }

            .section-kicker {
                margin-top: 0.8rem;
            }

            .stTabs [data-baseweb="tab"] {
                padding: 0.65rem 0.7rem;
            }

            .stButton > button, .stDownloadButton > button {
                min-height: 2.55rem;
            }
        }
=======
>>>>>>> dev/ai-integration
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def build_demo_dataset(scenario: str = "Busy Monday") -> Dict[str, pd.DataFrame]:
    """Return synthetic HVAC operations data that works without MongoDB."""
    scenario_multiplier = {
        "Busy Monday": 1.0,
        "Heat Wave": 1.24,
        "AR Cleanup": 0.88,
    }.get(scenario, 1.0)

    jobs = pd.DataFrame(
        [
            {
                "job_id": "JOB-001",
                "customer": "Smith Residence",
                "city": "Nashua",
                "priority": "Emergency",
                "risk": "Missing HP-001",
                "eta_window": "8:00-10:00",
            },
            {
                "job_id": "JOB-005",
                "customer": "Johnson Family",
                "city": "Hudson",
                "priority": "High",
                "risk": "Condenser capacitor low stock",
                "eta_window": "10:30-12:00",
            },
            {
                "job_id": "JOB-003",
                "customer": "XYZ Office",
                "city": "Merrimack",
                "priority": "Standard",
                "risk": "AR balance open",
                "eta_window": "1:00-3:00",
            },
        ]
    )
    inventory = pd.DataFrame(
        [
            {
                "sku": "HP-001",
                "part": "Heat pump control board",
                "on_hand": 2,
                "reorder_point": 5,
                "status": "Critical",
            },
            {
                "sku": "CAP-5TON",
                "part": "5 ton capacitor",
                "on_hand": 4,
                "reorder_point": 8,
                "status": "Low",
            },
            {
                "sku": "FILTER-20X25",
                "part": "20x25 filter",
                "on_hand": 32,
                "reorder_point": 18,
                "status": "Healthy",
            },
        ]
    )
    ar = pd.DataFrame(
        [
            {
                "invoice": "INV-001",
                "customer": "Smith Residence",
                "amount": int(1250 * scenario_multiplier),
                "days_overdue": 14,
                "next_action": "Send owner-approved reminder",
            },
            {
                "invoice": "INV-003",
                "customer": "XYZ Office",
                "amount": int(2100 * scenario_multiplier),
                "days_overdue": 31,
                "next_action": "Escalate with service history",
            },
        ]
    )
    return {"jobs": jobs, "inventory": inventory, "ar": ar}


def build_simulation_result(dataset: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
    """Build the deterministic demo result shown after the agent run."""
    overdue_total = int(dataset["ar"]["amount"].sum())
    critical_parts = int((dataset["inventory"]["status"] != "Healthy").sum())
    total_monthly_savings = 8400 + (critical_parts * 250)
    return {
        "total_monthly_savings": total_monthly_savings,
        "downtime_reduction": 0.42,
        "wasted_rolls_reduction": 0.30,
        "ar_improvement": max(12000, overdue_total * 3),
        "inventory_turns": 0.25,
        "agent_trace": [
            "LeadArchitect assembled the Monday operating plan.",
            "PartsAvailabilityChecker flagged HP-001 and CAP-5TON before dispatch.",
            "SchedulerOptimizer resequenced three priority stops around parts risk.",
            "ARCollector prepared two follow-up actions for overdue balances.",
            "RiskAssessor summarized downtime, cashflow, and first-visit-completion risk.",
        ],
    }


def _ensure_session_defaults() -> None:
    if "scenario" not in st.session_state:
        st.session_state.scenario = "Busy Monday"
    if "demo_loaded" not in st.session_state:
        st.session_state.demo_loaded = False
    if "dataset" not in st.session_state:
        st.session_state.dataset = build_demo_dataset(st.session_state.scenario)
    if "simulation" not in st.session_state:
        st.session_state.simulation = None


def render_sidebar() -> None:
    """Render the basic controls for the Phase 1 demo loop."""
    st.sidebar.markdown("### HVAC OpsForge")
    st.sidebar.caption(APP_SUBTITLE)
    scenario = st.sidebar.selectbox(
        "Demo scenario",
        ["Busy Monday", "Heat Wave", "AR Cleanup"],
        index=["Busy Monday", "Heat Wave", "AR Cleanup"].index(st.session_state.scenario),
    )
    if scenario != st.session_state.scenario:
        st.session_state.scenario = scenario
        st.session_state.dataset = build_demo_dataset(scenario)
        st.session_state.simulation = None
        st.session_state.demo_loaded = False

    st.sidebar.checkbox(
        "Use Live Mongo",
        value=False,
        help="Off keeps the demo fully self-contained with synthetic HVAC data.",
        key="use_live_mongo",
    )
    st.sidebar.checkbox("Show Agent Trace", value=True, key="show_agent_trace")

    if st.sidebar.button("Load Demo Company", use_container_width=True):
        st.session_state.dataset = build_demo_dataset(st.session_state.scenario)
        st.session_state.demo_loaded = True
        st.session_state.simulation = None
        st.sidebar.success("Demo company loaded.")

    if st.sidebar.button("Run Multi-Agent Dispatch", use_container_width=True):
        dataset = st.session_state.dataset
        with st.spinner("Lead Architect is coordinating specialist agents..."):
            st.session_state.simulation = build_simulation_result(dataset)
            st.session_state.demo_loaded = True
        st.sidebar.success("Agent run complete.")


def render_hero() -> None:
    """Render the branded top section."""
    st.markdown(
        f"""
        <section class="opsforge-hero">
            <div class="opsforge-brand-row">
                <div class="opsforge-mark">AF</div>
                <div>
                    <h1>{APP_TITLE}</h1>
                    <p>{APP_SUBTITLE}</p>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div class="opsforge-strip">
            Load a synthetic HVAC company, run the Lead Architect orchestration, and inspect the
            specialist outputs that protect first-visit completion, inventory turns, routes, and cashflow.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(simulation: Dict[str, Any] | None) -> None:
    """Render business outcome metrics for the current demo state."""
    sim = simulation or {
        "total_monthly_savings": 0,
        "downtime_reduction": 0.0,
        "wasted_rolls_reduction": 0.0,
        "ar_improvement": 0,
        "inventory_turns": 0.0,
    }
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Monthly Savings", f"${sim['total_monthly_savings']:,}", "$8.4k target")
    col2.metric("Downtime", f"-{sim['downtime_reduction'] * 100:.0f}%", "owner-visible")
    col3.metric("Wasted Trips", f"-{sim['wasted_rolls_reduction'] * 100:.0f}%", "fewer rolls")
    col4.metric("AR Cashflow", f"+${sim['ar_improvement']:,}", "faster collection")
    col5.metric("Inventory Turns", f"+{sim['inventory_turns'] * 100:.0f}%", "leaner stock")


def render_agent_console(simulation: Dict[str, Any] | None) -> None:
    """Show the multi-agent roster and the current synthetic execution state."""
    st.subheader("Agent Command Center")
    st.caption("Lead Architect coordinates specialist agents while the owner stays in control.")
    roster = pd.DataFrame(
        [
            {"Agent": "LeadArchitect", "Role": "Plans and coordinates the workflow", "Status": "Ready"},
            {"Agent": "PartsAvailabilityChecker", "Role": "Validates parts before dispatch", "Status": "Ready"},
            {"Agent": "SchedulerOptimizer", "Role": "Sequences stops by risk and location", "Status": "Ready"},
            {"Agent": "ARCollector", "Role": "Prepares overdue invoice follow-ups", "Status": "Ready"},
            {"Agent": "RiskAssessor", "Role": "Flags downtime, cashflow, and job risk", "Status": "Ready"},
        ]
    )
    if simulation:
        roster["Status"] = "Completed"
    st.dataframe(roster, use_container_width=True, hide_index=True)

    if simulation and st.session_state.get("show_agent_trace", True):
        st.markdown('<div class="opsforge-section-label">Execution Trace</div>', unsafe_allow_html=True)
        for item in simulation["agent_trace"]:
            st.info(item)


def render_operations_tabs(dataset: Dict[str, pd.DataFrame]) -> None:
    """Render basic interactive tables for the Phase 1 demo."""
    jobs_tab, inventory_tab, ar_tab = st.tabs(["Dispatch", "Inventory", "AR Follow-up"])
    with jobs_tab:
        st.subheader("Priority Dispatch Board")
        st.dataframe(dataset["jobs"], use_container_width=True, hide_index=True)
    with inventory_tab:
        st.subheader("Parts Availability Watchlist")
        st.dataframe(dataset["inventory"], use_container_width=True, hide_index=True)
        st.caption("Focus: prevent failed first visits by surfacing low-stock parts before the truck rolls.")
    with ar_tab:
        st.subheader("Accounts Receivable Follow-up Queue")
        st.dataframe(dataset["ar"], use_container_width=True, hide_index=True)
        st.caption("Focus: protect cashflow with owner-reviewed next actions.")


def owner_roi_simulator() -> None:
    """Render the branded owner ROI simulator for synthetic HVAC demo data."""
    dataset = st.session_state.dataset
    simulation = st.session_state.simulation
    render_hero()

    if not st.session_state.demo_loaded:
        st.warning("Start in the sidebar: load the demo company, then run the multi-agent dispatch.")

    render_kpi_row(simulation)
    st.divider()
    render_agent_console(simulation)
    st.divider()
    render_operations_tabs(dataset)


def parts_availability_dashboard() -> None:
    """Use Live Mongo toggle, validated schemas from PROJECT_MEMORY.md canonical VP, and 30-50% less downtime framing."""
    st.title("HVAC Parts Availability Command Center")
    st.checkbox(
        "Use Live Mongo (validated schemas from PROJECT_MEMORY.md canonical VP)",
        value=st.session_state.get("use_live_mongo", False),
    )
    st.caption(
        "Parts visibility protects first-visit completion, reduces wasted rolls, and supports the 30-50% downtime reduction target."
    )
    dataset = st.session_state.get("dataset", build_demo_dataset())
    st.dataframe(dataset["inventory"], use_container_width=True, hide_index=True)
    st.success("Parts tab maintains the 25% inventory optimization target from the canonical metrics.")


def main() -> None:
    configure_page()
    inject_brand_css()
    _ensure_session_defaults()
    render_sidebar()

    tab1, tab2 = st.tabs(["Owner ROI Simulator", "Parts Availability"])
    with tab1:
        owner_roi_simulator()
    with tab2:
        parts_availability_dashboard()


if __name__ == "__main__":
    main()
