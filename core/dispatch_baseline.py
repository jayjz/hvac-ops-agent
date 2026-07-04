"""Dispatch Baseline optimization pipeline for HVAC OpsForge."""

from __future__ import annotations

import asyncio
import json
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from core.agents import (
    ARCollectorAgent,
    AgentContext,
    InventoryForecasterAgent,
    LeadArchitect,
    RiskAssessorAgent,
    SchedulerOptimizerAgent,
)
from core.tools.mongodb_tools import mongodb_tools


PORTER_FORCES = [
    "Supplier power",
    "Buyer power",
    "Competitive rivalry",
    "Threat of substitutes",
    "Threat of new entrants",
]


async def build_dispatch_baseline(
    *,
    goals: List[str],
    project_path: Optional[str] = None,
    use_mongo: bool = False,
    mongo_tools: Any = None,
    job_id: Optional[str] = None,
    config_path: str | Path = "config.yaml",
) -> Dict[str, Any]:
    """Build a Dispatch Baseline from goals and synthetic or Mongo-backed data."""

    context = AgentContext(
        job_id=job_id or f"dispatch-baseline-{uuid4().hex[:10]}",
        project_path=project_path,
        goals=goals,
        metadata={"pipeline": "dispatch_baseline", "use_mongo": use_mongo},
    )
    memory: Dict[str, Any] = {}
    selected_mongo = mongo_tools if mongo_tools is not None else mongodb_tools
    mongo = selected_mongo if use_mongo else None
    common = {"config_path": config_path, "memory": memory, "tools": {"mongodb": mongo}}

    architect = LeadArchitect(**common)
    architect_result = await architect.run(context)
    if not architect_result.success:
        raise RuntimeError("; ".join(architect_result.errors))

    project_data = architect_result.data.get("project_data", {})
    execution_plan = architect_result.data.get("execution_plan", [])

    inventory_result = await InventoryForecasterAgent(**common).run(
        context,
        {
            "project_data": project_data,
            "execution_plan": execution_plan,
            "mongodb": mongo,
        },
    )
    inventory_data = inventory_result.data if inventory_result.success else {}

    risk_result = await RiskAssessorAgent(**common).run(
        context,
        {
            **inventory_data,
            "project_data": project_data,
            "mongodb": mongo,
        },
    )
    risk_data = risk_result.data if risk_result.success else {}

    schedule_result = await SchedulerOptimizerAgent(**common).run(
        context,
        {
            **inventory_data,
            **risk_data,
            "project_data": project_data,
            "mongodb": mongo,
        },
    )
    schedule_data = schedule_result.data if schedule_result.success else {}

    ar_result = await ARCollectorAgent(**common).run(
        context,
        {
            **inventory_data,
            **risk_data,
            **schedule_data,
            "mongodb": mongo,
        },
    )
    ar_data = ar_result.data if ar_result.success else {}

    return assemble_dispatch_baseline(
        goals=goals,
        project_data=project_data,
        execution_plan=execution_plan,
        inventory_data=inventory_data,
        risk_data=risk_data,
        schedule_data=schedule_data,
        ar_data=ar_data,
        data_source="mongo" if use_mongo else "synthetic",
    )


def build_dispatch_baseline_sync(**kwargs: Any) -> Dict[str, Any]:
    """Synchronous wrapper for scripts, notebooks, and CLI entrypoints."""

    return asyncio.run(build_dispatch_baseline(**kwargs))


def assemble_dispatch_baseline(
    *,
    goals: List[str],
    project_data: Dict[str, Any],
    execution_plan: List[Dict[str, Any]],
    inventory_data: Dict[str, Any],
    risk_data: Dict[str, Any],
    schedule_data: Dict[str, Any],
    ar_data: Dict[str, Any],
    data_source: str,
) -> Dict[str, Any]:
    """Normalize specialist outputs into the investor-facing Dispatch Baseline."""

    requirements = build_requirements_register(goals, project_data, inventory_data)
    schedule = normalize_schedule(schedule_data.get("optimized_schedule", {}), project_data)
    risks = rank_moat_risks(
        risk_data.get("risk_register", []),
        requirements=requirements,
        schedule=schedule,
        ar_items=ar_data.get("overdue_invoices", []),
    )
    ar_queue = prioritize_ar_queue(ar_data.get("overdue_invoices", []))
    roi_summary = build_roi_summary(
        requirements=requirements,
        risks=risks,
        schedule=schedule,
        ar_queue=ar_queue,
        inventory_orders=inventory_data.get("recommended_orders", []),
    )
    actions = recommend_actions(requirements, risks, schedule, ar_queue, roi_summary)

    baseline = {
        "report_type": "Dispatch Baseline",
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "data_source": data_source,
        "goals": goals,
        "summary": {
            "requirements_count": len(requirements),
            "high_risk_count": sum(1 for risk in risks if risk["severity"] == "High"),
            "planned_duration_days": schedule.get("duration_days"),
            "critical_path": schedule.get("critical_path", []),
            "ar_recovery_opportunity": roi_summary["ar_recovery_opportunity"],
            "estimated_roi": roi_summary["estimated_roi"],
        },
        "requirements_register": requirements,
        "risk_register": risks,
        "optimized_schedule": schedule,
        "ar_follow_up_queue": ar_queue,
        "roi_summary": roi_summary,
        "recommended_actions": actions,
        "execution_plan": execution_plan,
    }
    baseline["reports"] = {
        "markdown": render_dispatch_baseline_markdown(baseline),
        "json": json.dumps(to_jsonable(baseline, include_reports=False), indent=2, sort_keys=True),
    }
    return baseline


def build_requirements_register(
    goals: List[str],
    project_data: Dict[str, Any],
    inventory_data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    """Create a Jobs-to-be-Done aligned requirements register."""

    source = project_data.get("source", "synthetic")
    base_requirements = [
        (
            "Dispatch Reliability",
            "When dispatch demand changes, operations needs a prioritized work plan so crews protect SLA commitments.",
            "Schedule baseline covers all known critical-path tasks and at-risk jobs.",
            "Operations Manager",
            "High",
            "Schedule adherence",
        ),
        (
            "Parts Readiness",
            "When work is released, technicians need required parts staged so truck rolls are not wasted.",
            "Low-stock and job-critical parts are identified with order recommendations.",
            "Inventory Lead",
            "High",
            "First-time fix rate",
        ),
        (
            "Cash Discipline",
            "When invoices age past terms, finance needs a ranked follow-up queue so cash is recovered without distracting dispatch.",
            "Overdue invoices are prioritized by dollar value and aging.",
            "AR Owner",
            "Medium",
            "DSO reduction",
        ),
        (
            "Executive Control",
            "When risk exposure changes, leaders need a concise baseline so decisions are made before margin erodes.",
            "Top risks include probability, impact, moat exposure, mitigation, and owner action.",
            "General Manager",
            "High",
            "Gross margin protection",
        ),
    ]

    rows: List[Dict[str, Any]] = []
    for idx, (domain, jtbd, requirement, owner, priority, metric) in enumerate(base_requirements, start=1):
        rows.append(
            {
                "id": f"REQ-{idx:03d}",
                "domain": domain,
                "job_to_be_done": jtbd,
                "requirement": requirement,
                "owner": owner,
                "priority": priority,
                "success_metric": metric,
                "source": source,
                "value_driver": _value_driver(domain),
            }
        )

    for goal in goals[:4]:
        rows.append(
            {
                "id": f"REQ-{len(rows) + 1:03d}",
                "domain": "Strategic Goal",
                "job_to_be_done": "When leadership sets an operating goal, the dispatch baseline must translate it into owner-visible work.",
                "requirement": goal,
                "owner": "Executive Sponsor",
                "priority": "High",
                "success_metric": "Goal mapped to schedule, risk, AR, or inventory action.",
                "source": "user_goal",
                "value_driver": "Strategic alignment",
            }
        )

    for order in inventory_data.get("recommended_orders", [])[:3]:
        rows.append(
            {
                "id": f"REQ-{len(rows) + 1:03d}",
                "domain": "Inventory",
                "job_to_be_done": "When stock falls below dispatch need, purchasing needs a reorder signal before jobs slip.",
                "requirement": f"Stage or order {order.get('quantity', 0)} units of {order.get('part_name') or order.get('sku')}.",
                "owner": "Inventory Lead",
                "priority": "High" if order.get("urgency") == "high" else "Medium",
                "success_metric": "Parts available before scheduled work start.",
                "source": "inventory_forecast",
                "value_driver": "Avoided dispatch delay",
            }
        )

    return rows


def rank_moat_risks(
    risks: List[Dict[str, Any]],
    *,
    requirements: List[Dict[str, Any]],
    schedule: Dict[str, Any],
    ar_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Rank risks with a Porter's-style competitive moat lens."""

    if not risks:
        risks = [
            {"risk": "Dispatch reliability erosion", "probability": 0.34, "impact": 0.72, "category": "Operations"},
            {"risk": "Supplier lead-time leverage", "probability": 0.40, "impact": 0.70, "category": "Procurement"},
            {"risk": "Cash conversion drag", "probability": 0.30, "impact": 0.58, "category": "Financial"},
        ]

    duration_factor = min(float(schedule.get("duration_days") or 0) / 120.0, 0.25)
    ar_factor = min(len(ar_items) * 0.03, 0.15)
    requirement_factor = min(len(requirements) * 0.01, 0.12)
    rows: List[Dict[str, Any]] = []
    for idx, risk in enumerate(risks, start=1):
        probability = _safe_float(risk.get("probability"), 0.25)
        impact = _safe_float(risk.get("impact"), 0.50)
        category = str(risk.get("category") or "Operations")
        force = _porter_force(category, str(risk.get("risk", "")))
        moat_exposure = min(1.0, impact + duration_factor + ar_factor + requirement_factor)
        score = min(1.0, (probability * impact * 0.65) + (moat_exposure * 0.35))
        rows.append(
            {
                "rank": idx,
                "risk": risk.get("risk", f"Risk {idx}"),
                "category": category,
                "porter_force": force,
                "probability": round(probability, 3),
                "impact": round(impact, 3),
                "moat_exposure": round(moat_exposure, 3),
                "score": round(score, 3),
                "severity": "High" if score >= 0.42 else "Medium" if score >= 0.24 else "Low",
                "moat_impact": _moat_impact(force),
                "mitigation": risk.get("mitigation") or _default_mitigation(force),
            }
        )

    ranked = sorted(rows, key=lambda item: item["score"], reverse=True)
    for idx, row in enumerate(ranked, start=1):
        row["rank"] = idx
    return ranked


def normalize_schedule(schedule: Dict[str, Any], project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Return a schedule with tasks, duration, method, and critical path."""

    if schedule.get("tasks"):
        fixed = dict(schedule)
        fixed["tasks"] = sorted(schedule["tasks"], key=lambda item: _safe_float(item.get("start_day"), 0))
        fixed["duration_days"] = fixed.get("duration_days") or max(
            (_safe_float(task.get("finish_day"), 0) for task in fixed["tasks"]),
            default=0,
        )
        fixed["critical_path"] = fixed.get("critical_path") or _critical_path_from_tasks(fixed["tasks"])
        return fixed

    tasks = project_data.get("schedule") or [
        {"task": "Requirements validation", "duration_days": 5, "predecessors": []},
        {"task": "Equipment procurement", "duration_days": 25, "predecessors": ["Requirements validation"]},
        {"task": "Installation", "duration_days": 15, "predecessors": ["Equipment procurement"]},
        {"task": "Commissioning", "duration_days": 7, "predecessors": ["Installation"]},
    ]
    rows = _cpm_schedule(tasks)
    return {
        "method": "heuristic_cpm",
        "duration_days": max((_safe_float(row.get("finish_day"), 0) for row in rows), default=0),
        "tasks": rows,
        "critical_path": _critical_path_from_tasks(rows),
    }


def prioritize_ar_queue(invoices: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Prioritize AR follow-up by aging, dollars, and action urgency."""

    rows: List[Dict[str, Any]] = []
    now = datetime.utcnow()
    for idx, invoice in enumerate(invoices, start=1):
        invoice_id = invoice.get("invoice_id") or invoice.get("_id") or f"invoice-{idx}"
        amount = _safe_float(invoice.get("amount"), 0)
        due_date = _coerce_datetime(invoice.get("due_date"), now)
        days_overdue = int(invoice.get("days_overdue") or max((now - due_date).days, 0))
        priority_score = min(100.0, (amount / 100.0) + (days_overdue * 1.4))
        priority = "P1" if priority_score >= 80 else "P2" if priority_score >= 45 else "P3"
        rows.append(
            {
                "rank": idx,
                "invoice_id": str(invoice_id),
                "customer": invoice.get("customer_name") or invoice.get("customer_id") or "Customer",
                "amount": round(amount, 2),
                "days_overdue": days_overdue,
                "priority": priority,
                "priority_score": round(priority_score, 1),
                "recommended_action": _ar_action(priority, days_overdue),
            }
        )
    ranked = sorted(rows, key=lambda item: item["priority_score"], reverse=True)
    for idx, row in enumerate(ranked, start=1):
        row["rank"] = idx
    return ranked


def build_roi_summary(
    *,
    requirements: List[Dict[str, Any]],
    risks: List[Dict[str, Any]],
    schedule: Dict[str, Any],
    ar_queue: List[Dict[str, Any]],
    inventory_orders: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Estimate Dispatch Baseline ROI with transparent assumptions."""

    ar_total = sum(_safe_float(item.get("amount"), 0) for item in ar_queue)
    high_risks = [risk for risk in risks if risk.get("severity") == "High"]
    duration = _safe_float(schedule.get("duration_days"), 0)
    avoided_delay_days = min(max(duration * 0.08, len(high_risks) * 1.5), 10)
    avoided_delay_cost = avoided_delay_days * 1850
    ar_recovery = ar_total * 0.35
    margin_protection = sum(_safe_float(risk.get("score"), 0) for risk in high_risks) * 7500
    inventory_working_capital = len(inventory_orders) * 650
    estimated_value = ar_recovery + avoided_delay_cost + margin_protection + inventory_working_capital
    implementation_cost = max(3500.0, len(requirements) * 225.0)
    roi = (estimated_value - implementation_cost) / implementation_cost
    return {
        "ar_recovery_opportunity": round(ar_total, 2),
        "expected_ar_recovery": round(ar_recovery, 2),
        "avoided_delay_days": round(avoided_delay_days, 1),
        "avoided_delay_cost": round(avoided_delay_cost, 2),
        "margin_protection": round(margin_protection, 2),
        "inventory_working_capital": round(inventory_working_capital, 2),
        "estimated_value": round(estimated_value, 2),
        "implementation_cost": round(implementation_cost, 2),
        "estimated_roi": round(roi, 2),
        "assumptions": [
            "35% of overdue AR is recoverable through prioritized follow-up.",
            "Critical-path visibility avoids 8% of baseline schedule delay, capped at 10 days.",
            "High moat-exposure risks carry measurable gross margin protection value.",
        ],
    }


def recommend_actions(
    requirements: List[Dict[str, Any]],
    risks: List[Dict[str, Any]],
    schedule: Dict[str, Any],
    ar_queue: List[Dict[str, Any]],
    roi_summary: Dict[str, Any],
) -> List[str]:
    """Create concise executive actions from the baseline."""

    actions = [
        "Approve the Dispatch Baseline as the weekly operating control for service, inventory, AR, and risk review.",
        f"Protect the critical path: {' -> '.join(schedule.get('critical_path', [])[:5]) or 'No critical path available'}.",
    ]
    if risks:
        top = risks[0]
        actions.append(f"Assign an owner to top moat risk: {top['risk']} ({top['porter_force']}).")
    if ar_queue:
        actions.append(f"Start AR follow-up with {ar_queue[0]['customer']} for ${ar_queue[0]['amount']:,.2f}.")
    actions.append(f"Track estimated ROI of {roi_summary['estimated_roi']}x against value assumptions each week.")
    if len(requirements) > 6:
        actions.append("Use requirement owners to convert baseline findings into accountable weekly actions.")
    return actions


def render_dispatch_baseline_markdown(baseline: Dict[str, Any]) -> str:
    """Render an executive Markdown report."""

    summary = baseline["summary"]
    roi = baseline["roi_summary"]
    lines = [
        "# HVAC OpsForge Dispatch Baseline",
        "",
        f"Generated: {baseline['generated_at']}",
        f"Data source: {baseline['data_source']}",
        "",
        "## Executive Summary",
        "",
        f"- Requirements: {summary['requirements_count']}",
        f"- High risks: {summary['high_risk_count']}",
        f"- Planned duration: {summary['planned_duration_days']} days",
        f"- AR recovery opportunity: ${summary['ar_recovery_opportunity']:,.2f}",
        f"- Estimated ROI: {summary['estimated_roi']}x",
        "",
        "## Recommended Actions",
        "",
    ]
    lines.extend(f"- {action}" for action in baseline["recommended_actions"])
    lines.extend(["", "## Top Risks", ""])
    for risk in baseline["risk_register"][:5]:
        lines.append(
            f"- {risk['rank']}. {risk['risk']} | {risk['severity']} | {risk['porter_force']} | score {risk['score']}"
        )
    lines.extend(["", "## AR Follow-Up Queue", ""])
    for item in baseline["ar_follow_up_queue"][:5]:
        lines.append(
            f"- {item['rank']}. {item['customer']} | {item['priority']} | ${item['amount']:,.2f} | {item['days_overdue']} days"
        )
    lines.extend(
        [
            "",
            "## ROI Assumptions",
            "",
            f"- Expected AR recovery: ${roi['expected_ar_recovery']:,.2f}",
            f"- Avoided delay cost: ${roi['avoided_delay_cost']:,.2f}",
            f"- Margin protection: ${roi['margin_protection']:,.2f}",
        ]
    )
    lines.extend(f"- {assumption}" for assumption in roi["assumptions"])
    return "\n".join(lines)


def save_dispatch_baseline_reports(baseline: Dict[str, Any], output_dir: str | Path) -> Dict[str, str]:
    """Write Markdown and JSON reports to disk."""

    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    markdown_path = root / "dispatch_baseline.md"
    json_path = root / "dispatch_baseline.json"
    markdown_path.write_text(baseline["reports"]["markdown"], encoding="utf-8")
    json_path.write_text(baseline["reports"]["json"], encoding="utf-8")
    return {"markdown": str(markdown_path), "json": str(json_path)}


def to_jsonable(value: Any, *, include_reports: bool = True) -> Any:
    """Convert datetimes and nested values to JSON-compatible objects."""

    if isinstance(value, dict):
        return {
            key: to_jsonable(item, include_reports=include_reports)
            for key, item in value.items()
            if include_reports or key != "reports"
        }
    if isinstance(value, list):
        return [to_jsonable(item, include_reports=include_reports) for item in value]
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def _value_driver(domain: str) -> str:
    return {
        "Dispatch Reliability": "Revenue retention",
        "Parts Readiness": "Truck roll efficiency",
        "Cash Discipline": "Working capital",
        "Executive Control": "Margin protection",
    }.get(domain, "Operating leverage")


def _porter_force(category: str, risk_name: str) -> str:
    text = f"{category} {risk_name}".lower()
    if any(term in text for term in ["procurement", "supplier", "lead", "equipment", "parts"]):
        return "Supplier power"
    if any(term in text for term in ["ar", "invoice", "cash", "customer", "owner"]):
        return "Buyer power"
    if any(term in text for term in ["labor", "dispatch", "schedule", "field"]):
        return "Competitive rivalry"
    if any(term in text for term in ["controls", "automation", "technology"]):
        return "Threat of substitutes"
    if any(term in text for term in ["market", "new entrant", "competitor"]):
        return "Threat of new entrants"
    return PORTER_FORCES[len(text) % len(PORTER_FORCES)]


def _moat_impact(force: str) -> str:
    return {
        "Supplier power": "Weakens delivery reliability and gives vendors leverage over margin.",
        "Buyer power": "Increases cash drag and exposes service teams to price or payment pressure.",
        "Competitive rivalry": "Reduces responsiveness, making competitors look more reliable.",
        "Threat of substitutes": "Raises risk that controls or service alternatives displace the current offering.",
        "Threat of new entrants": "Compresses differentiation if operating discipline is not visible to customers.",
    }.get(force, "Creates avoidable operating exposure.")


def _default_mitigation(force: str) -> str:
    return {
        "Supplier power": "Qualify alternates, lock vendor commitments, and review long-lead items weekly.",
        "Buyer power": "Prioritize AR follow-up by amount and aging; escalate at defined thresholds.",
        "Competitive rivalry": "Protect dispatch SLAs with critical-path tracking and crew-ready work packages.",
        "Threat of substitutes": "Document controls integration value and commissioning proof points.",
        "Threat of new entrants": "Use baseline reporting to demonstrate reliability and execution maturity.",
    }.get(force, "Assign owner, due date, and weekly review cadence.")


def _ar_action(priority: str, days_overdue: int) -> str:
    if priority == "P1":
        return "Call decision maker today; send same-day written follow-up and escalation date."
    if priority == "P2":
        return "Send reminder and schedule owner follow-up within three business days."
    if days_overdue > 0:
        return "Send standard reminder and monitor next aging cycle."
    return "Monitor invoice status."


def _cpm_schedule(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    finish: Dict[str, int] = {}
    rows: List[Dict[str, Any]] = []
    unresolved = list(tasks)
    while unresolved:
        progressed = False
        for task in unresolved[:]:
            name = str(task.get("task") or task.get("name") or f"Task {len(rows) + 1}")
            predecessors = [str(item) for item in task.get("predecessors", [])]
            if all(pred in finish for pred in predecessors):
                start = max([finish[pred] for pred in predecessors] or [0])
                duration = int(_safe_float(task.get("duration_days"), 1))
                finish[name] = start + duration
                rows.append(
                    {
                        "task": name,
                        "start_day": start,
                        "finish_day": start + duration,
                        "duration_days": duration,
                    }
                )
                unresolved.remove(task)
                progressed = True
        if not progressed:
            raise ValueError("Schedule contains unresolved dependencies.")
    return rows


def _critical_path_from_tasks(tasks: List[Dict[str, Any]]) -> List[str]:
    if not tasks:
        return []
    ordered = sorted(tasks, key=lambda item: _safe_float(item.get("finish_day"), 0), reverse=True)
    max_finish = _safe_float(ordered[0].get("finish_day"), 0)
    path = [
        str(task.get("task"))
        for task in sorted(tasks, key=lambda item: _safe_float(item.get("start_day"), 0))
        if _safe_float(task.get("finish_day"), 0) <= max_finish
    ]
    return path


def _coerce_datetime(value: Any, default: datetime) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).replace(tzinfo=None)
        return value
    if isinstance(value, date):
        return datetime.combine(value, time.min)
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return default
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                return parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return parsed
        except ValueError:
            try:
                return datetime.combine(date.fromisoformat(raw[:10]), time.min)
            except ValueError:
                return default
    return default


def _safe_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
