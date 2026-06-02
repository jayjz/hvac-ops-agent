"""Specialist HVAC operations agents for HVAC OpsForge."""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Any, Dict, List

from core.agents.base import AgentContext, AgentResult, BaseAgent


class InventoryForecasterAgent(BaseAgent):
    """Forecast inventory needs based on upcoming jobs and historical usage."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="inventory_forecaster", **kwargs)

    async def execute(self, context: AgentContext, payload: Dict[str, Any]) -> AgentResult:
        project_data = payload.get("project_data", {})
        await self.report_progress(context, 0.20, "Analyzing upcoming jobs and inventory levels.")
        requirements = await asyncio.to_thread(self._extract_requirements, project_data, context.goals)
        await self.report_progress(context, 0.70, "Forecasting parts needs and reorder points.")
        self.remember("requirements_register", requirements)
        await self.report_progress(context, 0.90, "Inventory forecast ready.")
        return AgentResult(agent=self.name, success=True, data={"requirements_register": requirements})

    def _extract_requirements(self, project_data: Dict[str, Any], goals: List[str]) -> List[Dict[str, Any]]:
        text = " ".join(str(item.get("content", "")) for item in project_data.get("files", []))
        domains = {
            "HVAC": ["ahu", "hvac", "chiller", "boiler", "commissioning"],
            "Controls": ["bas", "automation", "plc", "scada", "controls"],
            "Construction": ["installation", "site", "permit", "submittal"],
            "Financial": ["budget", "cost", "contingency", "procurement"],
        }
        requirements = []
        idx = 1
        for domain, keywords in domains.items():
            if any(keyword in text.lower() for keyword in keywords) or project_data.get("synthetic"):
                requirements.append(
                    {
                        "id": f"REQ-{idx:03d}",
                        "domain": domain,
                        "statement": f"Define, approve, and track {domain.lower()} scope requirements.",
                        "priority": "High" if domain in {"HVAC", "Controls"} else "Medium",
                        "acceptance_criteria": (
                            "Owner sign-off, traceable deliverable, and measurable completion evidence."
                        ),
                    }
                )
                idx += 1
        for goal in goals:
            requirements.append(
                {
                    "id": f"REQ-{idx:03d}",
                    "domain": "User Goal",
                    "statement": goal,
                    "priority": "High",
                    "acceptance_criteria": "Goal is mapped to schedule, risk, owner, and completion metric.",
                }
            )
            idx += 1
        return requirements


class RiskAssessorAgent(BaseAgent):
    """Assess operational risks: low stock, delayed payments, scheduling conflicts."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="risk_assessor", **kwargs)

    async def execute(self, context: AgentContext, payload: Dict[str, Any]) -> AgentResult:
        await self.report_progress(context, 0.20, "Analyzing inventory, AR, and scheduling data.")
        risk_register = await asyncio.to_thread(self._forecast, payload)
        await self.report_progress(context, 0.70, "Identifying operational risks and opportunities.")
        self.remember("risk_register", risk_register)
        await self.report_progress(context, 0.90, "Risk assessment complete.")
        return AgentResult(agent=self.name, success=True, data={"risk_register": risk_register})

    def _forecast(self, payload: Dict[str, Any]) -> List[Dict[str, Any]]:
        import pandas as pd

        requirements = payload.get("requirements_register", [])
        project_data = payload.get("project_data", {})
        budget = project_data.get("budget", {"labor": 75000, "materials": 150000, "contingency": 20000})
        budget_total = sum(float(value) for value in budget.values())

        base = pd.DataFrame(
            [
                {"risk": "Long-lead equipment delay", "probability": 0.42, "impact": 0.75, "category": "Procurement"},
                {"risk": "Controls integration defect", "probability": 0.35, "impact": 0.70, "category": "Automation"},
                {"risk": "Field labor constraint", "probability": 0.30, "impact": 0.55, "category": "Construction"},
                {"risk": "Scope gap or late owner decision", "probability": 0.28, "impact": 0.62, "category": "Stakeholder"},
                {
                    "risk": "Budget contingency burn",
                    "probability": min(0.65, 20000 / max(budget_total, 1)),
                    "impact": 0.65,
                    "category": "Financial",
                },
            ]
        )
        requirement_factor = min(0.15, len(requirements) * 0.015)
        base["score"] = ((base["probability"] + requirement_factor) * base["impact"]).clip(upper=1.0)
        base["severity"] = base["score"].apply(
            lambda score: "High" if score >= 0.35 else "Medium" if score >= 0.18 else "Low"
        )
        base["mitigation"] = base["category"].map(
            {
                "Procurement": "Validate submittals early, track vendor commitments weekly, and approve alternates.",
                "Automation": "Run interface tests before commissioning and reserve controls engineering support.",
                "Construction": "Level labor loading and protect shutdown windows.",
                "Stakeholder": "Create decision log with dated owner approvals.",
                "Financial": "Tie contingency releases to approved risk events.",
            }
        )
        return base.sort_values("score", ascending=False).to_dict(orient="records")


class SchedulerOptimizerAgent(BaseAgent):
    """Optimize technician job scheduling considering skills, location, and urgency."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="scheduler", **kwargs)

    async def execute(self, context: AgentContext, payload: Dict[str, Any]) -> AgentResult:
        await self.report_progress(context, 0.20, "Loading technician schedules and job requirements.")
        schedule = await asyncio.to_thread(self._optimize, payload)
        await self.report_progress(context, 0.70, "Optimizing routes and technician assignments.")
        self.remember("optimized_schedule", schedule)
        await self.report_progress(context, 0.90, "Optimized schedule ready.")
        return AgentResult(agent=self.name, success=True, data={"optimized_schedule": schedule})

    def _optimize(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        project_data = payload.get("project_data", {})
        tasks = project_data.get("schedule") or [
            {"task": "Requirements validation", "duration_days": 5, "predecessors": []},
            {"task": "Procurement", "duration_days": 20, "predecessors": ["Requirements validation"]},
            {"task": "Installation", "duration_days": 15, "predecessors": ["Procurement"]},
            {"task": "Commissioning", "duration_days": 7, "predecessors": ["Installation"]},
        ]
        try:
            return self._optimize_with_pulp(tasks)
        except Exception as exc:
            self.logger.warning("PuLP optimization failed, using CPM fallback: %s", exc)
            return self._cpm(tasks)

    def _optimize_with_pulp(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        import pulp

        names = [str(task["task"]) for task in tasks]
        durations = {str(task["task"]): int(task.get("duration_days", 1)) for task in tasks}
        starts = pulp.LpVariable.dicts("start", names, lowBound=0, cat="Continuous")
        makespan = pulp.LpVariable("makespan", lowBound=0, cat="Continuous")
        problem = pulp.LpProblem("pm_schedule", pulp.LpMinimize)
        problem += makespan
        for task in tasks:
            name = str(task["task"])
            problem += starts[name] + durations[name] <= makespan
            for predecessor in task.get("predecessors", []):
                if predecessor in starts:
                    problem += starts[name] >= starts[predecessor] + durations[predecessor]
        problem.solve(pulp.PULP_CBC_CMD(msg=False))
        rows = [
            {
                "task": name,
                "start_day": float(starts[name].value() or 0),
                "finish_day": float((starts[name].value() or 0) + durations[name]),
                "duration_days": durations[name],
            }
            for name in names
        ]
        return {
            "method": "pulp",
            "duration_days": float(makespan.value() or 0),
            "tasks": rows,
            "critical_path": self._critical_path(tasks),
        }

    def _cpm(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        finish: Dict[str, int] = {}
        rows = []
        unresolved = list(tasks)
        while unresolved:
            progress = False
            for task in unresolved[:]:
                predecessors = task.get("predecessors", [])
                if all(pred in finish for pred in predecessors):
                    start = max([finish[pred] for pred in predecessors] or [0])
                    duration = int(task.get("duration_days", 1))
                    finish[str(task["task"])] = start + duration
                    rows.append(
                        {
                            "task": task["task"],
                            "start_day": start,
                            "finish_day": start + duration,
                            "duration_days": duration,
                        }
                    )
                    unresolved.remove(task)
                    progress = True
            if not progress:
                raise ValueError("Schedule contains unresolved dependencies.")
        return {
            "method": "cpm",
            "duration_days": max(finish.values() or [0]),
            "tasks": rows,
            "critical_path": self._critical_path(tasks),
        }

    def _critical_path(self, tasks: List[Dict[str, Any]]) -> List[str]:
        by_name = {str(task["task"]): task for task in tasks}
        memo: Dict[str, tuple[int, List[str]]] = {}

        def score(name: str) -> tuple[int, List[str]]:
            if name in memo:
                return memo[name]
            task = by_name[name]
            predecessors = [pred for pred in task.get("predecessors", []) if pred in by_name]
            if not predecessors:
                result = (int(task.get("duration_days", 1)), [name])
            else:
                best = max((score(pred) for pred in predecessors), key=lambda item: item[0])
                result = (best[0] + int(task.get("duration_days", 1)), best[1] + [name])
            memo[name] = result
            return result

        if not by_name:
            return []
        return max((score(name) for name in by_name), key=lambda item: item[0])[1]


class ARCollectorAgent(BaseAgent):
    """Manage accounts receivable: identify overdue invoices and draft reminders."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(name="ar_collector", **kwargs)

    async def execute(self, context: AgentContext, payload: Dict[str, Any]) -> AgentResult:
        await self.report_progress(context, 0.20, "Fetching AR aging and overdue invoices.")
        report = await asyncio.to_thread(self._generate, payload)
        await self.report_progress(context, 0.70, "Drafting reminder communications.")
        self.remember("pm_report", report)
        await self.report_progress(context, 0.90, "AR collection actions ready.")
        return AgentResult(agent=self.name, success=True, data={"pm_report": report})

    def _generate(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        risks = payload.get("risk_register", [])
        requirements = payload.get("requirements_register", [])
        schedule = payload.get("optimized_schedule", {})
        chart_path = self._risk_chart(risks)
        high_risks = [risk for risk in risks if risk.get("severity") == "High"]
        return {
            "summary": "HVAC operations analysis complete: inventory forecast, risk assessment, and schedule optimization.",
            "requirements_count": len(requirements),
            "high_risk_count": len(high_risks),
            "planned_duration_days": schedule.get("duration_days"),
            "critical_path": schedule.get("critical_path", []),
            "recommended_actions": [
                "Review inventory forecast and place orders for low-stock items.",
                "Follow up on overdue invoices identified in AR aging.",
                "Confirm technician assignments for upcoming jobs.",
            ],
            "risk_chart_path": chart_path,
        }

    def _risk_chart(self, risks: List[Dict[str, Any]]) -> str | None:
        if not risks:
            return None
        try:
            import matplotlib

            matplotlib.use("Agg")
            import matplotlib.pyplot as plt

            labels = [str(risk["risk"])[:28] for risk in risks]
            scores = [float(risk.get("score", 0)) for risk in risks]
            fig, ax = plt.subplots(figsize=(9, 4))
            ax.barh(labels, scores, color="#2f6f73")
            ax.set_xlabel("Risk score")
            ax.set_title("Top Operational Risks")
            fig.tight_layout()
            output = Path(tempfile.gettempdir()) / "hvac_ops_risk_chart.png"
            fig.savefig(output)
            plt.close(fig)
            return str(output)
        except Exception as exc:
            self.logger.warning("Risk chart generation failed: %s", exc)
            return None
